#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
A distutils/setuptools command extension, so that building applications is as
easy as "python setup.py bdist_launcher".
"""

import distutils.cmd
from distutils import log
import launcher_tool.copy_launcher
import launcher_tool.launcher_zip
import launcher_tool.create_python27_minimal
import launcher_tool.download_python3_minimal
from launcher_tool.download_python3_minimal import URL_32, URL_64
import sys
import os
import pkgutil
import zipfile


def write_launcher(filename, main_script, use_py2, use_64bits):
    """\
    helper function that writes a launcher exe with the appended __main__.py
    and support files
    """
    with open(filename, 'wb') as exe:
        launcher_tool.copy_launcher.copy_launcher(exe, use_py2, use_64bits)
        with zipfile.ZipFile(exe, 'a', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('__main__.py', main_script.encode('utf-8'))
            archive.writestr('launcher.py', pkgutil.get_data('launcher_tool', 'launcher.py'))


class LauncherCommand(distutils.cmd.Command):
    """\
    Additional command for distutils/setuptools.
    """

    description = "Build windows executables"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        #~ print(dir(self.distribution))
        #~ print(self.distribution.scripts)
        #~ print(self.distribution.requires)
        use_python27 = (sys.version_info.major == 2)
        is_64bits = sys.maxsize > 2**32  # recommended by docs.python.org "platform" module

        dest_dir = os.path.join('dist', 'launcher{}-{}'.format(
            '27' if use_python27 else '3',
            '64' if is_64bits else '32'))
        log.info('installing to {}'.format(dest_dir))
        self.mkpath(dest_dir)
        
        log.info('preparing a wheel file of application')
        self.run_command('bdist_wheel')
        log.info('installing wheel of application (with dependencies)')
        self.spawn([sys.executable, '-m', 'pip', 'install',
                    '--disable-pip-version-check',
                    '--prefix', dest_dir,
                    '--ignore-installed', #'--no-index',
                    '--find-links=dist', self.distribution.get_name()])

        if hasattr(self.distribution, 'entry_points') and self.distribution.entry_points:
            if 'console_scripts' in self.distribution.entry_points:
                #~ print(self.distribution.entry_points['console_scripts'])
                for combination in self.distribution.entry_points['console_scripts']:
                    name, entry_point = combination.split('=')
                    name = name.strip()
                    entry_point = entry_point.strip()
                    filename = os.path.join(dest_dir, '{}.exe'.format(name))
                    self.execute(write_launcher,
                                 (filename,
                                  launcher_tool.launcher_zip.make_main(entry_point=entry_point),
                                  use_python27, is_64bits),
                                 'writing launcher {}'.format(filename))

        if hasattr(self.distribution, 'scripts'):
            for source in self.distribution.scripts:
                filename = os.path.join(dest_dir, '{}.exe'.format(os.path.basename(source)))
                script = open(source).read()
                # append users' script to the launcher boot code
                main_script = '{}\n{}'.format(launcher_tool.launcher_zip.make_main(), script)
                self.execute(write_launcher,
                             (filename, main_script, use_python27, is_64bits),
                             'writing launcher {}'.format(filename))

        if use_python27:
            if not os.path.exists(os.path.join(dest_dir, 'python27-minimal')):
                launcher_tool.create_python27_minimal.copy_python(
                    os.path.join(dest_dir, 'python27-minimal'))
            else:
                log.info('python27-minimal installation already present')
        else:
            if not os.path.exists(os.path.join(dest_dir, 'python3-minimal')):
                log.info('extracting python minimal installation')
                launcher_tool.download_python3_minimal.extract(
                    URL_64 if is_64bits else URL_32,
                    os.path.join(dest_dir, 'python3-minimal'))
            else:
                log.info('python3-minimal installation already present')
