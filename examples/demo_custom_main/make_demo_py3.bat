set DIST=dist3
set PYTHONPATH=..\..
py -3 -m launcher_tool -o %DIST%/demo1_py3.exe --main demo1.py
py -3 -m launcher_tool.download_python3_minimal -d %DIST%
