=========
 Changes
=========

0.9
===
- support for 64 bit Python 2.7

0.8
===
- support variables in --extend-sys-path (e.g. $SELF)

0.7
===
- support variables in --run-path (e.g. $SELF)
- new function: launcher.hide_console()
- new function: launcher.hide_console_until_error()
- update download_python3_minimal to download 3.5.2

0.6
===
- more configurability for bdist_launcher (--python-minimal, --bin-dir)
- per-file configuration possibility for bdist_launcher 

0.5.1
=====
- added missing example (demo_app) to distribution
- fix: extend_sys_path attribute is now a parameter

0.5
===
- bdist_launcher distuils/setuptools command added
- new example: demo_app for use with bdist_launcher
- fix: close stdio channels before closing cosole window, fixes an issue with
  subprocess

0.4
===
- 64 bit support for Python 3
- improve error message if Python DLL is not found
- fix: redo restore_sys_argv to avoid quotes around argv[0]

0.3.1
=====
re-release for pypi (fix descriptions in setup.py)

0.3
===
- add --extend-sys-path argument
- allow glob patterns for --add-file and --add-zip
- other fixes
