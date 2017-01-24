set PY2_64_INC=C:\Python27-64
set PY2_32_INC=C:\Python27

echo %PY2_64_INC%
echo %PY2_32_INC%

windres -F pe-i386 launcher27.rc -O coff -o launcher27-32.res
gcc -m32 -o ..\..\launcher_tool\launcher27-32.exe launcher27.c launcher27-32.res -std=gnu99 -Wall -I %PY2_32_INC%\\include
strip ..\..\launcher_tool\launcher27-32.exe 

windres -F pe-x86-64 launcher27.rc -O coff -o launcher27-64.res
gcc -m64 -o ..\..\launcher_tool\launcher27-64.exe launcher27.c launcher27-64.res -std=gnu99 -Wall -I %PY2_64_INC%\\include
strip ..\..\launcher_tool\launcher27-64.exe
