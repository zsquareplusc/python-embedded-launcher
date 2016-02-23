set PYTHONPATH=..\..
python -m launcher_tool -o dist/demo1.exe --main demo1.py
if not exist python27-minimal   python -m launcher_tool.create_python_minimal -d dist
