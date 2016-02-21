rem python -m pip wheel pyserial
python ../launcher_tool.py -o demo2.exe --main demo2.py -e wheelhouse/pyserial-3.0.1-py2-none-any.whl
if not exist python27-minimal   python ../create_python_minimal.py
