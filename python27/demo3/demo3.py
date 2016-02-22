# first configure the launcher: restore command line and add exe dir to sys.path
import launcher
launcher.patch_sys_path()
launcher.restore_sys_argv()

import sample_application
sample_application.main()
