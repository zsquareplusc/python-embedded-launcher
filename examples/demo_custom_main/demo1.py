import sys
import os
import launcher

print """
sys.argv = {sys.argv}

sys.executable = {sys.executable}

os location = {os.__file__} (Python's Landmark file)
""".format(sys=sys, os=os)

print 'sys.path ='
for entry in sys.path:
    print '  {}'.format(entry)

print
print 'PATH ='
for entry in os.environ['PATH'].split(';'):
    print '  {}  {}'.format(entry, 'OK' if os.path.exists(entry) else 'MISSING!!')

launcher.restore_sys_argv()
print 'sys.argv = {}'.format(sys.argv)

raw_input('[ENTER]')
