import sys

from .ffmpeg_progress_yield import FfmpegProgress


def main():
    if len(sys.argv) <= 1:
        raise RuntimeError("You need to pass an ffmpeg command as CLI arguments")

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
