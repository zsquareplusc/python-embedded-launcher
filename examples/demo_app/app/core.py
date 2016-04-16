#!python
# encoding: utf-8
"""\
Sample application
"""
import sys
import ctypes

def main():
    try:
        import launcher
    except ImportError:
        pass
    else:
        launcher.close_console()
    ctypes.windll.user32.MessageBoxW(
        None,
        u'APP is running!\nParameters:\n{}'.format('\n'.join(sys.argv)),
        u'demo_app',
        0x40)

if __name__ == '__main__':
    main()
