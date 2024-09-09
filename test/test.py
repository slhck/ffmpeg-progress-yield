#!/usr/bin/env pytest
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))

from ffmpeg_progress_yield import FfmpegProgress  # noqa: E402

_TEST_ASSET = os.path.join(os.path.dirname(__file__), "test.mp4")


class TestLibrary:
    cmd = [
        "ffmpeg",
        "-i",
        _TEST_ASSET,
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

    unknown_dur_cmd = [
        "ffmpeg",
        "-re",
        "-f",
        "lavfi",
        "-i",
        "testsrc=d=10",
        "-t",
        "5",
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

    def test_unknown_dur(self):
        ff = FfmpegProgress(TestLibrary.unknown_dur_cmd)
        progresses = set([0.0])
        for progress in ff.run_command_with_progress():
            progresses.add(progress)
        # assert that we get only 0 and 100% progress since we have no implicit duration
        assert list(progresses) == [0, 100]

    def test_manual_dur(self):
        ff = FfmpegProgress(TestLibrary.unknown_dur_cmd)
        progresses = set([0.0])
        for progress in ff.run_command_with_progress(duration_override=5):
            progresses.add(progress)
        # assert that we get more than just 0 and 100
        assert len(progresses) > 2

    def test_getting_stderr(self):
        ff = FfmpegProgress(TestLibrary.cmd)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0 and ff.stderr is not None:
                assert len(ff.stderr) > 0
                break

    def test_quit(self):
        ff = FfmpegProgress(TestLibrary.cmd)
        proc = None
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0:
                proc = ff.process
                ff.quit()
                break
        # expect that no ffmpeg process is running after this test after sleeping for 1 second
        assert proc is not None
        proc.wait()
        assert proc.returncode == -9

    def test_quit_gracefully(self):
        ff = FfmpegProgress(TestLibrary.cmd)
        proc = None
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0 and ff.process is not None:
                proc = ff.process
                ff.quit_gracefully()
                break
        # expect that no ffmpeg process is running after this test after sleeping for 1 second
        assert proc is not None
        assert proc.returncode == 0

    def test_stderr_callback(self):
        def stderr_callback(line):
            print(line)

        ff = FfmpegProgress(TestLibrary.cmd)
        ff.set_stderr_callback(stderr_callback)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0:
                break

    def test_progress_with_loglevel_error(self):
        cmd = TestLibrary.cmd
        cmd.extend(["-loglevel", "error"])
        ff = FfmpegProgress(cmd)
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0:
                assert 0 < progress < 100
                break


class TestProgress:
    def test_progress(self):
        cmd = [
            "python3",
            "-m",
            "ffmpeg_progress_yield",
            "ffmpeg",
            "-i",
            _TEST_ASSET,
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
        assert "100.0/100" in ret.stderr or "100/100" in ret.stderr


class TestAsyncLibrary:
    cmd = TestLibrary.cmd

    @pytest.mark.asyncio
    async def test_async_library(self):
        ff = FfmpegProgress(TestAsyncLibrary.cmd)
        elapsed = 0
        async for progress in ff.async_run_command_with_progress():
            print(f"{progress}/100")
            assert progress >= elapsed
            elapsed = progress
        # assert that we get 100% progress
        assert elapsed == 100

    @pytest.mark.asyncio
    async def test_async_quit(self):
        ff = FfmpegProgress(TestAsyncLibrary.cmd)
        proc = None
        async for progress in ff.async_run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0:
                proc = ff.process
                await ff.async_quit()
                break
        assert proc is not None
        await proc.wait()
        assert proc.returncode != 0

    @pytest.mark.asyncio
    async def test_async_quit_gracefully(self):
        ff = FfmpegProgress(TestAsyncLibrary.cmd)
        proc = None
        async for progress in ff.async_run_command_with_progress():
            print(f"{progress}/100")
            if progress > 0 and ff.process is not None:
                proc = ff.process
                await ff.async_quit_gracefully()
                break
        assert proc is not None
        assert proc.returncode == 0
