@set PATH=C:\TDM-GCC-32\bin;%PATH%
@for /f %%i in ('py -3 -c "import sys,os; print(os.path.dirname(sys.executable))"') do set PY3_INC=%%i
windres launcher3.rc -O coff -o launcher3.res
gcc -o ..\..\launcher_tool\launcher3.exe launcher3.c launcher3.res -DUNICODE -Wall -I %PY3_INC%\\include
