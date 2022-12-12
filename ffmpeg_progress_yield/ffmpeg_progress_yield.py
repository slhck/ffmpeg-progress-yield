import subprocess
import re
from typing import Generator, List, Union

def to_ms(string: Union[None, str] = None, precision: Union[None, int] = None, **kwargs) -> float:
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
        self.process = None
        self.stderr_callback = None

    def set_stderr_callback(self, callback):
        """
        Set a callback function to be called on stderr output.
        The callback function must accept a single string argument.
        Note that this is called on every line of stderr output, so it can be called a lot.
        Also note that stdout/stderr are joined into one stream, so you might get stdout output in the callback.
        """
        if not callable(callback) or len(callback.__code__.co_varnames) != 1:
            raise ValueError(
                "Callback must be a function that accepts only one argument"
            )

        self.stderr_callback = callback

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
            [self.cmd[0]] + ["-progress", "-", "-nostats"] + self.cmd[1:]
        )

        stderr = []

        self.process = subprocess.Popen(
            cmd_with_progress,
            stdin=subprocess.PIPE,  # Apply stdin isolation by creating separate pipe.
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
            **popen_kwargs
        )

        yield 0

        while True:
            if self.process.stdout is None:
                continue

            stderr_line = (
                self.process.stdout.readline().decode("utf-8", errors="replace").strip()  # type: ignore
            )

            if self.stderr_callback:
                self.stderr_callback(stderr_line)

            if stderr_line == "" and self.process.poll() is not None:
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

        if self.process.returncode != 0:
            raise RuntimeError(
                "Error running command {}: {}".format(self.cmd, str("\n".join(stderr)))
            )

        yield 100
        self.process = None

    def quit_gracefully(self):
        """
        Quit the ffmpeg process by sending 'q'
        Raises an exception if no process is found.
        """
        if self.process is None:
            raise RuntimeError("No process found. Did you run the command?")

        self.process.communicate(input="q".encode())  # type: ignore

    def quit(self):
        """
        Quit the ffmpeg process by sending SIGKILL.
        Raises an exception if no process is found.
        """
        if self.process is None:
            raise RuntimeError("No process found. Did you run the command?")

        self.process.kill()
