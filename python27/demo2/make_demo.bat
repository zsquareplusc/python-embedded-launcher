set PYTHONUSERBASE=dist
REM ~ python -m pip wheel -r requirements.txt
python -m pip install --user --ignore-installed --find-links=wheelhouse --no-index -r requirements.txt
python ../launcher_tool.py -o dist/demo2.exe --main demo2.py
if not exist python27-minimal   python ../create_python_minimal.py -d dist
