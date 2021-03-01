# ffmpeg-progress

[![PyPI version](https://img.shields.io/pypi/v/ffmpeg-progress.svg)](https://img.shields.io/pypi/v/ffmpeg-progress)

Run an ffmpeg command with its progress yielded.

Contents:

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Caveats](#caveats)
- [License](#license)

-------------

## Requirements

-   Python 3.6 or higher
-   ffmpeg v3.1 or above from <http://ffmpeg.org/> installed in your \$PATH

## Installation

    pip3 install ffmpeg-progress

Or download this repository, then run `pip install .`.

## Usage

In your Python project, import the helper class and run `run_command_with_progress`:

```python
from ffmpeg_progress import FfmpegProgress

cmd = [
    "ffmpeg", "-i", "test/test.mp4", "-c:v", "libx264", "-vf", "scale=1920x1080", "-preset", "fast", "-f", "null", "/dev/null",
]

ff = FfmpegProgress(cmd)
for progress in ff.run_command_with_progress():
    print(f"{progress}/100")
```

The command will yield the current progress in percent.

If you have `tqdm` installed, you can create a fancy progress bar:

```python
from tqdm import tqdm
from ffmpeg_progress import FfmpegProgress

cmd = [
    "ffmpeg", "-i", "test/test.mp4", "-c:v", "libx264", "-vf", "scale=1920x1080", "-preset", "fast", "-f", "null", "/dev/null",
]

ff = FfmpegProgress(cmd)
with tqdm(total=100, position=1, desc="Test") as pbar:
    for progress in ff.run_command_with_progress():
        pbar.update(progress - pbar.n)
```

You can get the output of the command with the `.stderr` attribute of the `FfmpegProgress` class.

## Caveats

Some notes:

1. The progress cannot be extracted for sources that don't have a duration (e.g. live sources).

2. Currently, we do not differentiate between `stderr` and `stdout`. This means progress will be mixed with the ffmpeg log.

## License

The MIT License (MIT)

Copyright (c) 2021 Werner Robitza

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
