import subprocess
import re


def to_ms(string=None, precision=None, **kwargs):
    """
    Convert a string to milliseconds.
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

    def __init__(self, cmd, dry_run=False) -> None:
        self.cmd = cmd
        self.dry_run = dry_run
        self.stderr = None

    def run_command_with_progress(self):
        """
        Run an ffmpeg command, trying to capture the process output and calculate
        the duration / progress.
        Yields the progress in percent.
        """
        if self.cmd[0] != "ffmpeg":
            raise RuntimeError("Command is not an ffmpeg command!")

        if self.dry_run:
            return

        total_dur = None

        cmd_with_progress = (
            [self.cmd[0]] + ["-progress", "-", "-nostats"] + self.cmd[1:]
        )

        stderr = []

        p = subprocess.Popen(
            cmd_with_progress,
            stdin=subprocess.PIPE,  # Apply stdin isolation by creating separate pipe.
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False,
        )

        while True:
            stderr_line = p.stdout.readline().decode("utf8", errors="replace").strip()

            if stderr_line == "" and p.poll() is not None:
                break

            stderr.append(stderr_line.strip())

            self.stderr = "\n".join(stderr)

            if not total_dur and FfmpegProgress.DUR_REGEX.search(stderr_line):
                total_dur = FfmpegProgress.DUR_REGEX.search(stderr_line).groupdict()
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
