set DIST=dist3
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse  python -m pip wheel -r requirements.txt
py -3 -m pip install --user --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
py -3 -m launcher_tool -o %DIST%/miniterm_py3.exe -e serial.tools.miniterm:main
if not exist %DIST%\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d %DIST%
