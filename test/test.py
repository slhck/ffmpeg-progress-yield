#!/usr/bin/env pytest
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ffmpeg_progress_yield import FfmpegProgress  # noqa: E402


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

    def test_getting_stderr(self):
        ff = FfmpegProgress(TestLibrary.cmd)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0 and ff.stderr is not None:
                assert len(ff.stderr) > 0
                break

    def test_quit(self):
        ff = FfmpegProgress(TestLibrary.cmd)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0:
                ff.quit()
                break
        # expect that no ffmpeg process is running after this test after sleeping for 1 second
        time.sleep(1)
        assert len(subprocess.run(["pgrep", "ffmpeg"], capture_output=True).stdout) == 0

    def test_quit_gracefully(self):
        ff = FfmpegProgress(TestLibrary.cmd)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0 and ff.process is not None:
                ff.quit_gracefully()
                break
        # expect that no ffmpeg process is running after this test after sleeping for 1 second
        time.sleep(1)
        assert len(subprocess.run(["pgrep", "ffmpeg"], capture_output=True).stdout) == 0

    def test_stderr_callback(self):
        def stderr_callback(line):
            print(line)

        ff = FfmpegProgress(TestLibrary.cmd)
        ff.set_stderr_callback(stderr_callback)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0:
                break


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
