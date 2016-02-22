# first configure the launcher: restore command line and add update sys.path
import launcher
launcher.patch_sys_path(['Python27/site-packages'])
launcher.restore_sys_argv()

import serial.tools.miniterm
serial.tools.miniterm.main()