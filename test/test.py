#!/usr/bin/env pytest
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ffmpeg_progress_yield import FfmpegProgress


class TestLibrary:
    cmd = [
            "ffmpeg",
            "-i",
            "test/test.mp4",
            "-c:v",
            "libx264",
            "-vf",
            "scale=1920x1080",
            "-preset",
            "fast",
            "-f",
            "null",
            "/dev/null",
        ]

    def test_library(self):    
        ff = FfmpegProgress(TestLibrary.cmd)
        elapsed = 0
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            assert progress >= elapsed
            elapsed = progress
        # assert that we get 100% progress
        assert elapsed == 100

    def test_quit(self):
        ff = FfmpegProgress(TestLibrary.cmd)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 50:
                ff.quit()
                break
        # expect that no ffmpeg process is running after this test
        assert len(subprocess.run(["pgrep", "ffmpeg"], capture_output=True).stdout) == 0

class TestProgress:
    def test_progress(self):
        cmd = [
            "python3",
            "-m",
            "ffmpeg_progress_yield",
            "ffmpeg",
            "-i",
            "test/test.mp4",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-f",
            "null",
            "/dev/null",
        ]
        ret = subprocess.run(cmd, capture_output=True, universal_newlines=True)
        assert "0/100" in ret.stderr
        assert "100/100" in ret.stderr
