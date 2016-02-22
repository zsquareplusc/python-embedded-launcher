rem python -m pip wheel pyserial
python ../launcher_tool.py -o dist/demo2.exe --main demo2.py -e pyserial
if not exist python27-minimal   python ../create_python_minimal.py -d dist
