import sys

from . import __version__ as version
from .ffmpeg_progress_yield import FfmpegProgress


def main() -> None:
    if len(sys.argv) <= 1 or sys.argv[1] in ("-h", "-help"):
        print(
            f"ffmpeg-progress-yield v{version}\n\n"
            "Usage: ffmpeg-progress-yield [-h] ffmpeg-command\n\n"
            "Arguments:\n"
            " ffmpeg-command:     Any ffmpeg command. Do not quote this argument.\n\n"
            "Options:\n -h/--help:          Show this help and exit."
        )
        sys.exit(1)

    ff = FfmpegProgress(sys.argv[1:])

    try:
        from tqdm import tqdm

        with tqdm(total=100, position=1, desc="Test") as pbar:
            for progress in ff.run_command_with_progress():
                pbar.update(progress - pbar.n)
    except ImportError:
        for progress in ff.run_command_with_progress():
            print(f"{progress}/100")

    print(ff.stderr)


if __name__ == "__main__":
    main()
