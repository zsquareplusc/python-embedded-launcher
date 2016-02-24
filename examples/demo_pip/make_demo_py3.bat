set PYTHONPATH=..\..
set PYTHONUSERBASE=dist
if not exist wheelhouse  python -m pip wheel -r requirements.txt
py -3 -m pip install --user --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
py -3 -m launcher_tool -o dist/miniterm_py3.exe -x serial.tools.miniterm:main
if not exist dist\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d dist
