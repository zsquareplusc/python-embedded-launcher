set PYTHONPATH=..\..
python -m launcher_tool -o dist/demo_wx_py27.exe -e sample_application:main --add-file sample_application.py
python -m launcher_tool.create_python27_minimal -d dist
if not exist dist\wx   python copy_wx.py dist
