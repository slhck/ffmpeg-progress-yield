import os
import re
import subprocess
from typing import Any, Callable, Iterator, List, Optional, Union


def to_ms(**kwargs: Union[float, int, str]) -> int:
    hour = int(kwargs.get("hour", 0))
    minute = int(kwargs.get("min", 0))
    sec = int(kwargs.get("sec", 0))
    ms = int(kwargs.get("ms", 0))

    return (hour * 60 * 60 * 1000) + (minute * 60 * 1000) + (sec * 1000) + ms


def _probe_duration(cmd: List[str]) -> Optional[int]:
    """
    Get the duration via ffprobe from input media file
    in case ffmpeg was run with loglevel=error.

    Args:
        cmd (List[str]): A list of command line elements, e.g. ["ffmpeg", "-i", ...]

    Returns:
        Optional[int]: The duration in milliseconds.
    """
    file_names = []
    for i, arg in enumerate(cmd):
        if arg == "-i":
            file_name = cmd[i + 1]

            # filter for filenames that we can probe, i.e. regular files
            if os.path.isfile(file_name):
                file_names.append(file_name)

    if len(file_names) == 0:
        return None

    durations = []

    for file_name in file_names:
        try:
            output = subprocess.check_output(
                [
                    "ffprobe",
                    "-loglevel",
                    "error",
                    "-hide_banner",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    file_name,
                ],
                universal_newlines=True,
            )
            durations.append(int(float(output.strip()) * 1000))
        except Exception:
            # TODO: add logging
            return None

    return max(durations) if "-shortest" not in cmd else min(durations)


def _uses_error_loglevel(cmd: List[str]) -> bool:
    try:
        idx = cmd.index("-loglevel")
        if cmd[idx + 1] == "error":
            return True
        else:
            return False
    except ValueError:
        return False


def _get_inputs_with_options(cmd: List[str]) -> List[List[str]]:
    """
    Collect all inputs with their options.
    For example, input is:

        ffmpeg -i input1.mp4 -i input2.mp4 -i input3.mp4 -filter_complex ...

    Output is:

        [
            ["-i", "input1.mp4"],
            ["-i", "input2.mp4"],
            ["-i", "input3.mp4"],
        ]

    Another example:

        ffmpeg -f lavfi -i color=c=black:s=1920x1080 -loop 1 -i image.png -filter_complex ...

    Output is:

        [
            ["-f", "lavfi", "-i", "color=c=black:s=1920x1080"],
            ["-loop", "1", "-i", "image.png"],
        ]
    """
    inputs = []
    prev_index = 0
    for i, arg in enumerate(cmd):
        if arg == "-i":
            inputs.append(cmd[prev_index : i + 2])
            prev_index = i + 2

    return inputs


class FfmpegProgress:
    DUR_REGEX = re.compile(
        r"Duration: (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})"
    )
    TIME_REGEX = re.compile(
        r"out_time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})"
    )

    def __init__(self, cmd: List[str], dry_run: bool = False) -> None:
        """Initialize the FfmpegProgress class.

        Args:
            cmd (List[str]): A list of command line elements, e.g. ["ffmpeg", "-i", ...]
            dry_run (bool, optional): Only show what would be done. Defaults to False.
        """
        self.cmd = cmd
        self.stderr: Union[str, None] = None
        self.dry_run = dry_run
        self.process: Any = None
        self.stderr_callback: Union[Callable[[str], None], None] = None
        self.base_popen_kwargs = {
            "stdin": subprocess.PIPE,  # Apply stdin isolation by creating separate pipe.
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "universal_newlines": False,
        }

    def set_stderr_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set a callback function to be called on stderr output.
        The callback function must accept a single string argument.
        Note that this is called on every line of stderr output, so it can be called a lot.
        Also note that stdout/stderr are joined into one stream, so you might get stdout output in the callback.

        Args:
            callback (Callable[[str], None]): A callback function that accepts a single string argument.
        """
        if not callable(callback) or len(callback.__code__.co_varnames) != 1:
            raise ValueError(
                "Callback must be a function that accepts only one argument"
            )

        self.stderr_callback = callback

    def run_command_with_progress(
        self, popen_kwargs=None, duration_override: Union[float, None] = None
    ) -> Iterator[float]:
        """
        Run an ffmpeg command, trying to capture the process output and calculate
        the duration / progress.
        Yields the progress in percent.

        Args:
            popen_kwargs (dict, optional): A dict to specify extra arguments to the popen call, e.g. { creationflags: CREATE_NO_WINDOW }
            duration_override (float, optional): The duration in seconds. If not specified, it will be calculated from the ffmpeg output.

        Raises:
            RuntimeError: If the command fails, an exception is raised.

        Yields:
            Iterator[float]: A generator that yields the progress in percent.
        """
        if self.dry_run:
            return self.cmd

        total_dur: Union[None, int] = None
        if _uses_error_loglevel(self.cmd):
            total_dur = _probe_duration(self.cmd)

        if duration_override is not None:
            total_dur = int(duration_override * 1000)

        cmd_with_progress = (
            [self.cmd[0]] + ["-progress", "-", "-nostats"] + self.cmd[1:]
        )

        # collect all inputs with their options, e.g.
        inputs_with_options = _get_inputs_with_options(self.cmd)

        stderr = []
        base_popen_kwargs = self.base_popen_kwargs.copy()
        if popen_kwargs is not None:
            base_popen_kwargs.update(popen_kwargs)

        self.process = subprocess.Popen(
            cmd_with_progress,
            **base_popen_kwargs,
        )  # type: ignore

        yield 0

        input_idx = 0

        while True:
            if self.process.stdout is None:
                continue

            stderr_line = (
                self.process.stdout.readline().decode("utf-8", errors="replace").strip()
            )

            if self.stderr_callback:
                self.stderr_callback(stderr_line)

            if stderr_line == "" and self.process.poll() is not None:
                break

            stderr.append(stderr_line.strip())

            self.stderr = "\n".join(stderr)

            # assign the total duration if it was found. this can happen multiple times for multiple inputs,
            # in which case we have to determine the overall duration by taking the min/max (dependent on -shortest being present)
            if (
                current_dur_match := self.DUR_REGEX.search(stderr_line)
            ) and duration_override is None:
                input_options = inputs_with_options[input_idx]

                current_dur_ms: int = to_ms(**current_dur_match.groupdict())
                # if the previous line had "image2", it's a single image and we assume a really short intrinsic duration (4ms),
                # but if it's a loop, we assume infinity
                if "image2" in stderr[-2] and "-loop 1" in " ".join(input_options):
                    # infinity
                    current_dur_ms = 2**64
                if "-shortest" in self.cmd:
                    total_dur = (
                        min(total_dur, current_dur_ms)
                        if total_dur is not None
                        else current_dur_ms
                    )
                else:
                    total_dur = (
                        max(total_dur, current_dur_ms)
                        if total_dur is not None
                        else current_dur_ms
                    )

                input_idx += 1

            if (
                progress_time := FfmpegProgress.TIME_REGEX.search(stderr_line)
            ) and total_dur is not None:
                elapsed_time = to_ms(**progress_time.groupdict())
                yield min(max(round(elapsed_time / total_dur * 100, 2), 0), 100)

        if self.process is None or self.process.returncode != 0:
            _pretty_stderr = "\n".join(stderr)
            raise RuntimeError(f"Error running command {self.cmd}: {_pretty_stderr}")

        yield 100
        self.process = None

    def quit_gracefully(self) -> None:
        """
        Quit the ffmpeg process by sending 'q'

        Raises:
            RuntimeError: If no process is found.
        """
        if self.process is None:
            raise RuntimeError("No process found. Did you run the command?")

        self.process.communicate(input=b"q")
        self.process.kill()
        self.process = None

    def quit(self) -> None:
        """
        Quit the ffmpeg process by sending SIGKILL.

        Raises:
            RuntimeError: If no process is found.
        """
        if self.process is None:
            raise RuntimeError("No process found. Did you run the command?")

        self.process.kill()
        self.process = None
