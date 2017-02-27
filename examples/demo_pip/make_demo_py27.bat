set DIST=dist27
set PYTHONPATH=..\..
if not exist wheelhouse  python -m pip wheel -w wheelhouse -r requirements.txt
python -m pip install --prefix=%DIST% --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
python -m launcher_tool -o %DIST%/miniterm_py27.exe -e serial.tools.miniterm:main --wait-on-error
python -m launcher_tool.create_python27_minimal -d %DIST%
