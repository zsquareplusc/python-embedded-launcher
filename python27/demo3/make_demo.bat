python ../launcher_tool.py -o demo3.exe --main demo3.py sample_application.py
if not exist python27-minimal   python ../create_python_minimal.py
if not exist wx-3.0-msw   python copy_wx.py
