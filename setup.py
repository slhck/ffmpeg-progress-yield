#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# read version string
with open(path.join(here, 'ffmpeg_progress_yield', '__init__.py')) as version_file:
    version = eval(version_file.read().split("\n")[2].split("=")[1].strip())

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the history from the CHANGELOG file
with open(path.join(here, 'CHANGELOG.md'), encoding='utf-8') as f:
    history = f.read()

setup(
    name='ffmpeg-progress-yield',
    version=version,
    description="Run an ffmpeg command with progress",
    long_description=long_description + '\n\n' + history,
    long_description_content_type='text/markdown',
    author="Werner Robitza",
    author_email='werner.robitza@gmail.com',
    url='https://github.com/slhck/ffmpeg-progress-yield',
    packages=['ffmpeg_progress_yield'],
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords='ffmpeg',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    entry_points={
        'console_scripts': [
            'ffmpeg-progress-yield = ffmpeg_progress_yield.__main__:main'
        ]
    },
)
