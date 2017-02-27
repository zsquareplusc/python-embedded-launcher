set DIST=dist3
set PYTHONPATH=..\..
if not exist wheelhouse  python -m pip wheel -w wheelhouse -r requirements.txt
py -3 -m pip install --prefix=%DIST% --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
py -3 -m launcher_tool -o %DIST%/miniterm_py3.exe -e serial.tools.miniterm:main --wait-on-error
py -3 -m launcher_tool.download_python3_minimal -d %DIST%
