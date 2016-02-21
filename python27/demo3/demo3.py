# first configure the launcher: restore command line
import launcher
#~ launcher.patch_sys_path()
launcher.restore_sys_argv()

# add the directory containing wx to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(sys.executable), 'wx-3.0-msw'))

import sample_application
sample_application.main()
