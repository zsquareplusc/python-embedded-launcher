python ../launcher_tool.py -o dist/demo3.exe -x sample_application:main sample_application.py
if not exist dist\python27-minimal   python ../create_python_minimal.py -d dist
if not exist dist\wx   python copy_wx.py dist
