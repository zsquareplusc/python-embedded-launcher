# first configure the launcher: restore command line and add wheels to sys.path
import launcher
launcher.add_wheels()
launcher.restore_sys_argv()

# now we can use the wheels directly (as long it is a pure python wheel and compatible)
import serial.tools.miniterm
serial.tools.miniterm.main()