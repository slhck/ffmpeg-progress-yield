# Changelog


## v0.10.0 (2024-11-18)

* Fix: ensure percentage is always in float.


## v0.9.1 (2024-09-16)

* Fix: the logic of the option --progress-only.


## v0.9.0 (2024-09-16)

* Docs: add @LaunchLee as a contributor.

* Chore: Add an option to print progress only in cli usage.

  This option makes the output cleaner when doing batch conversions.

* Code cleanup, refactoring.

  To avoid having to juggle around variables


## v0.8.1 (2024-09-09)

* Fix type-checks.


## v0.8.0 (2024-09-09)

* Add async support.


## v0.7.9 (2024-08-14)

* Docs: add @ammgws as a contributor.

* Fix typing error.

* Chore: remove unused dependency.

* Fix badge link.


## v0.7.8 (2023-06-01)

* Image handling.

  Check if image2 inputs use looping or not, and set duration to infinity if needed


## v0.7.6 (2023-05-30)

* Always use duration_override if present.


## v0.7.5 (2023-05-30)

* Fix duration for multiple inputs, fixes #13.

* Fix 'Test' string in tqdm.


## v0.7.4 (2023-05-06)

* Fix: round percentage numbers.


## v0.7.3 (2023-05-05)

* Update readme.

* Add progress as percent, fixes #12.


## v0.7.2 (2023-03-04)

* Do not print input information when probing, addresses #10.


## v0.7.1 (2023-02-24)

* Fix types in CI.

* Remove unneeded import.

* Typo.

* Docs: add @kskadart as a contributor.

* Fix formatting.

* Fix types.

* Feat(ffprobe): FEAT-0001 try to get duration by ffprobe in case if loglevel=error.

* Fix CI file.


## v0.7.0 (2023-01-24)

* Add duration override to API.

* Remove manifest.in.

* Add mypy settings.


## v0.6.1 (2022-12-18)

* Add py.typed.

* Move API docs to existing section.


## v0.6.0 (2022-12-17)

* Link to API docs.

* Add API docs.

* Add export.

* Bump requirements to python 3.8 or higher.

* Document methods.

* Remove unused import.

* Docs: add @WyattBlue as a contributor.

* Docs: add @slhck as a contributor.

* Unhide to_ms.

* Add type hints + simplify.

* Add python CI badge.

* Fix quit tests.

* Add all-contributors.

* Add pytest to dev requirements.

* Add github workflows.

* Formatting.

* Fix a few type and formatting errors.


## v0.5.0 (2022-12-12)

* Add stderr callback method.

* Update README.

* Add graceful quit method.

* Add a GIF in the readme.


## v0.4.0 (2022-12-11)

* Add a quit method, fixes #4.


## v0.3.0 (2022-08-02)

* Update python requirements.


## v0.2.0 (2021-11-21)

* Add a usage option.


## v0.1.2 (2021-08-14)

* Remove universal_newlines for Windows compat.


## v0.1.1 (2021-07-01)

* Remove stats_period option for backwards compatibility, fixes #2.


## v0.1.0 (2021-06-30)

* Format code with black.

* Yield 0 in progress and improve logic.

* Set universal_newlines to true and add kwargs support.

* Increase stats period.

* Document method.

* Add typing.

* Also check for 0 in output.

* Update gitignore.

* Drop python 3.5 support.

* Update badge link.


## v0.0.4 (2021-03-10)

* Add python_requires to setup.py.


## v0.0.3 (2021-03-06)

* Remove release script.


## v0.0.2 (2021-03-06)

* Fix release script.

* Remove support for older versions.

* Format setup.py.

* Remove requirement for command to start with ffmpeg.

* Add link to similar project.

* Add changelog.

* Rename project.

* Initial commit.


