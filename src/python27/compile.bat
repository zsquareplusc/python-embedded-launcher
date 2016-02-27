@set PATH=C:\TDM-GCC-32\bin;%PATH%
@for /f %%i in ('python -c "import sys,os; print(os.path.dirname(sys.executable))"') do set PY2_INC=%%i
windres launcher27.rc -O coff -o launcher27.res
gcc -o ..\..\launcher_tool\launcher27.exe launcher27.c launcher27.res -Wall -I %PY2_INC%\\include
