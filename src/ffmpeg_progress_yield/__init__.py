from importlib import metadata

from .ffmpeg_progress_yield import FfmpegProgress

try:
    __version__ = metadata.version("ffmpeg-progress-yield")
except metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["FfmpegProgress"]
