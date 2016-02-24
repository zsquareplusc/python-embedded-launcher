import sys
import os
import launcher

sys.path.append(sys.argv[1])

sys.stdout.write("""
sys.argv = {sys.argv}

sys.executable = {sys.executable}

os location = {os.__file__} (Python's Landmark file)
""".format(sys=sys, os=os))
try:

    sys.stdout.write('sys.path =\n')
    for entry in sys.path:
        sys.stdout.write('  {}\n'.format(entry))

    sys.stdout.write('\nPATH =\n')
    for entry in os.environ['PATH'].split(';'):
        sys.stdout.write('  {}  {}\n'.format(entry, '[OK]' if os.path.exists(entry) else '[MISSING]'))

    launcher.restore_sys_argv()
    sys.stdout.write('sys.argv = {}\n'.format(sys.argv))
    sys.stdout.write('END.\n')
finally:
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        raw_input('[ENTER]')    # python 2
    except:
        input('[ENTER]')        # python 3
