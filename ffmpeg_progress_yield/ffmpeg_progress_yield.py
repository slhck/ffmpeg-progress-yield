import subprocess
import re
from typing import Generator, List


def to_ms(string: str = None, precision: int = None, **kwargs) -> float:
    """
    Convert a string to milliseconds.
    You can either pass a string, or a set of keyword args ("hour", "min", "sec", "ms") to convert.
    If "precision" is set, the result is rounded to the number of decimals given.
    From: https://gist.github.com/Hellowlol/5f8545e999259b4371c91ac223409209
    """
    if string:
        hour = int(string[0:2])
        minute = int(string[3:5])
        sec = int(string[6:8])
        ms = int(string[10:11])
    else:
        hour = int(kwargs.get("hour", 0))
        minute = int(kwargs.get("min", 0))
        sec = int(kwargs.get("sec", 0))
        ms = int(kwargs.get("ms", 0))

    result = (hour * 60 * 60 * 1000) + (minute * 60 * 1000) + (sec * 1000) + ms
    if precision and isinstance(precision, int):
        return round(result, precision)
    return result


class FfmpegProgress:
    DUR_REGEX = re.compile(
        r"Duration: (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})"
    )
    TIME_REGEX = re.compile(
        r"out_time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})"
    )

    def __init__(self, cmd: List[str], dry_run=False) -> None:
        """Initialize the FfmpegProgress class.

        Args:
            cmd (List[str]): A list of command line elements, e.g. ["ffmpeg", "-i", ...]
            dry_run (bool, optional): Only show what would be done. Defaults to False.
        """
        self.cmd = cmd
        self.dry_run = dry_run
        self.stderr = None

    def run_command_with_progress(self, popen_kwargs={}) -> Generator[int, None, None]:
        """
        Run an ffmpeg command, trying to capture the process output and calculate
        the duration / progress.
        Yields the progress in percent.

        Args:
            popen_kwargs (dict): A dict to specify extra arguments to the popen call, e.g. { creationflags: CREATE_NO_WINDOW }
        """
        if self.dry_run:
            return

        total_dur = None

        cmd_with_progress = (
            [self.cmd[0]]
            + ["-progress", "-", "-nostats"]
            + self.cmd[1:]
        )

        stderr = []

        p = subprocess.Popen(
            cmd_with_progress,
            stdin=subprocess.PIPE,  # Apply stdin isolation by creating separate pipe.
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
            **popen_kwargs
        )

        yield 0

        while True:
            if p.stdout is None:
                continue

            stderr_line = p.stdout.readline().decode("utf-8", errors="replace").strip()

            if stderr_line == "" and p.poll() is not None:
                break

            stderr.append(stderr_line.strip())

            self.stderr = "\n".join(stderr)

            total_dur_match = FfmpegProgress.DUR_REGEX.search(stderr_line)
            if total_dur is None and total_dur_match:
                total_dur = total_dur_match.groupdict()
                total_dur = to_ms(**total_dur)
                continue
            if total_dur:
                progress_time = FfmpegProgress.TIME_REGEX.search(stderr_line)
                if progress_time:
                    elapsed_time = to_ms(**progress_time.groupdict())
                    yield int(elapsed_time / total_dur * 100)

        if p.returncode != 0:
            raise RuntimeError(
                "Error running command {}: {}".format(self.cmd, str("\n".join(stderr)))
            )

        yield 100
