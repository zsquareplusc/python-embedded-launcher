set PYTHONPATH=..\..
set PYTHONUSERBASE=dist
if not exist wheelhouse  python -m pip wheel -r requirements.txt
python -m pip install --user --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
python -m launcher_tool -o dist/miniterm_py27.exe -x serial.tools.miniterm:main
if not exist dist\python27-minimal   python -m launcher_tool.create_python27_minimal -d dist
