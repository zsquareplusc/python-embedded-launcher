@set PATH=C:\TDM-GCC-64\bin;%PATH%
@for /f %%i in ('py -3 -c "import sys,os; print(os.path.dirname(sys.executable))"') do set PY3_INC=%%i
windres -F pe-i386 launcher3.rc -O coff -o launcher3-32.res
windres -F pe-x86-64 launcher3.rc -O coff -o launcher3-64.res
gcc -m32 -o ..\..\launcher_tool\launcher3-32.exe launcher3.c launcher3-32.res -DUNICODE -Wall -I %PY3_INC%\\include
gcc -m64 -o ..\..\launcher_tool\launcher3-64.exe launcher3.c launcher3-64.res -DUNICODE -Wall -I %PY3_INC%\\include
strip ..\..\launcher_tool\launcher3-32.exe ..\..\launcher_tool\launcher3-64.exe