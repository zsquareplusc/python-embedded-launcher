@set PATH=C:\TDM-GCC-32\bin;%PATH%
windres launcher27.rc -O coff -o launcher27.res
gcc -o ..\..\launcher_tool\launcher27.exe launcher27.c launcher27.res -Wall -I c:\\Python27\\include
