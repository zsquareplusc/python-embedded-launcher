import sys
import os

print "sys.argv", sys.argv
print "sys.executable", sys.executable
print "original sys.path"
for entry in sys.path:
    print " ", entry

print "appending to sys.path\n  ", os.path.dirname(sys.executable)
sys.path.append(os.path.dirname(sys.executable))

print
print 'OS =', os.__file__
print 'PATH ='
for entry in os.environ['PATH'].split(';'):
    print ' ', entry, 'OK' if os.path.exists(entry) else 'MISSING!!'

# get original command via Windows API
import ctypes
import shlex
commandline = ctypes.c_wchar_p(ctypes.windll.kernel32.GetCommandLineW())
sys.argv = shlex.split(commandline.value, posix=False)
print 'sys.argv =', sys.argv
