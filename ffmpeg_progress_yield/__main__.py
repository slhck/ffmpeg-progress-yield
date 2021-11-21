import sys

from .ffmpeg_progress_yield import FfmpegProgress
from .import __version__ as version


def print_usage():
    print(f"ffmpeg-progress-yield v{version}")
    print()
    print("Usage: ffmpeg-progress-yield [-h] ffmpeg-command")
    print("")
    print("Arguments:")
    print(" ffmpeg-command:     Any ffmpeg command. Do not quote this argument.")
    print("")
    print("Options:")
    print(" -h/--help:          Show this help and exit.")

def main():
    if len(sys.argv) <= 1:
        print_usage()
        sys.exit(1)

    if sys.argv[1] in ["-h", "--help"]:
        print_usage()
        sys.exit(0)

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
