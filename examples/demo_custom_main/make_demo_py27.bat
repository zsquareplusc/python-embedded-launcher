set DIST=dist27
set PYTHONPATH=..\..
python -m launcher_tool -o %DIST%/demo1_py27.exe --main demo1.py
python -m launcher_tool.create_python27_minimal -d %DIST%
