python ../launcher_tool.py -o dist/demo3.exe --main demo3.py sample_application.py
if not exist dist\python27-minimal   python ../create_python_minimal.py -d dist
if not exist dist\wx-3.0-msw   python copy_wx.py dist
