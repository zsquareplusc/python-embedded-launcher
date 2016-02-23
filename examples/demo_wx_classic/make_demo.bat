set PYTHONPATH=..\..
python -m launcher_tool -o dist/demo3.exe -x sample_application:main sample_application.py
if not exist dist\python27-minimal   python -m launcher_tool.create_python_minimal -d dist
if not exist dist\wx   python copy_wx.py dist
