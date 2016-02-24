set DIST=dist27
set PYTHONPATH=..\..
set PYTHONUSERBASE=%DIST%
if not exist wheelhouse  python -m pip wheel -r requirements.txt
python -m pip install --user --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
python -m launcher_tool -o %DIST%/miniterm_py27.exe -e serial.tools.miniterm:main
if not exist %DIST%\python27-minimal   python -m launcher_tool.create_python27_minimal -d %DIST%
