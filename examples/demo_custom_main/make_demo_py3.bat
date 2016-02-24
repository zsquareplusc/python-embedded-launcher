set PYTHONPATH=..\..
py -3 -m launcher_tool -o dist/demo1_py3.exe --main demo1.py
if not exist dist\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d dist
