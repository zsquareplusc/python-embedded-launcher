set DIST=dist3
set PYTHONPATH=..\..
REM ~ if not exist wheelhouse  python -m pip wheel -w wheelhouse -r requirements.txt
REM ~ py -3 -m pip install --prefix=%DIST% --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
py -3 setup.py bdist_wheel 
py -3 -m pip install --prefix=%DIST% --ignore-installed --no-index --find-links=dist sample_application
py -3 -m launcher_tool -o %DIST%/app.exe -m app --wait-on-error
if not exist %DIST%\python3-minimal   py -3 -m launcher_tool.download_python3_minimal -d %DIST%
