#!/usr/bin/env pytest
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ffmpeg_progress_yield import FfmpegProgress


class TestLibrary:
    def test_library(self):
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
        ff = FfmpegProgress(cmd)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")


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
            "-vf",
            "scale=1920x1080",
            "-preset",
            "fast",
            "-f",
            "null",
            "/dev/null",
        ]
        ret = subprocess.run(cmd, capture_output=True, universal_newlines=True)
        assert "100/100" in ret.stderr
