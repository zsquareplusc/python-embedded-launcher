set PYTHONPATH=..\..
python -m launcher_tool -o dist/demo1_py27.exe --main demo1.py
if not exist dist\python27-minimal   python -m launcher_tool.create_python27_minimal -d dist
