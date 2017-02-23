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
import sys
import os
import pkgutil
import zipfile

import launcher_tool.copy_launcher
import launcher_tool.launcher_zip
import launcher_tool.resource_editor
import launcher_tool.create_python27_minimal
import launcher_tool.download_python3_minimal


def convert_boolean_option(value):
    """convert a string representation of a boolean to a bool"""
    return value.strip().lower() in ('1', 'true', 'yes')


class bdist_launcher(distutils.cmd.Command):  # pylint: disable=too-many-instance-attributes
    """\
    Additional command for distutils/setuptools.
    """
    #pylint: disable=invalid-name,attribute-defined-outside-init

    description = "Build windows executables"

    user_options = [
        ('icon=', None, 'filename of icon to use'),
        ('python-minimal=', None, 'change the location of the python-minimal distribution'),
        ('extend-sys-path=', 'p', 'add search pattern(s) for files added to '
                                  'sys.path (separated by "{}")'.format(os.pathsep)),
        ('wait-at-exit', None, 'do not close console window automatically'),
        ('wait-on-error', None, 'wait if there is an exception'),
        ('bin-dir', None, 'put binaries in subdirectory /bin'),
    ]

    boolean_options = ['wait-at-exit', 'wait-on-error', 'bin-dir']

    def initialize_options(self):
        self.icon = None
        self.python_minimal = None
        self.bin_dir = False
        self.extend_sys_path = None
        self.wait_at_exit = False
        self.wait_on_error = False

    def finalize_options(self):
        if self.python_minimal is not None and self.bin_dir:
            raise ValueError('Can not combine --python-minmal and --bin-dir options')

        self.use_python27 = (sys.version_info.major == 2)
        self.is_64bits = sys.maxsize > 2**32  # recommended by docs.python.org "platform" module
        # convert path string to a list of strings
        if self.extend_sys_path is None:
            self.extend_sys_path_list = ()
        else:
            self.extend_sys_path_list = self.extend_sys_path.split(os.pathsep)
        self.dest_dir = os.path.join('dist', 'launcher{}-{}'.format(
            '27' if self.use_python27 else '3',
            '64' if self.is_64bits else '32'))

    def get_option_dict_for_file(self, filename):
        """\
        combine options (from command line and bdist_launcher setings in setup.cfg)
        with options that can be specified per file
        """
        options = dict(self.distribution.get_option_dict('bdist_launcher'))  # copy!
        options.update(self.distribution.get_option_dict('bdist_launcher:{}'.format(os.path.basename(filename))))
        resulting_options = {}
        for k, v in options.items():
            if k.replace('_', '-') in self.boolean_options:
                resulting_options[k] = convert_boolean_option(v[1])
            else:
                resulting_options[k] = v[1]
        return resulting_options

    def copy_customized_launcher(self, fileobj, options):
        """\
        Copy launcher to build dir and run the resource editor, output result
        to given fileobj.
        """
        build_dir = os.path.join('build', 'bdist_launcher.{}.{}'.format(
            '27' if self.use_python27 else '3',
            '64' if self.is_64bits else '32'))
        self.mkpath(build_dir)
        launcher_temp = os.path.join(build_dir, 'launcher.exe')
        with open(launcher_temp, 'wb') as temp_exe:
            launcher_tool.copy_launcher.copy_launcher(temp_exe, self.use_python27, self.is_64bits)
        if 'icon' in options:
            log.info('changing icon to: {}'.format(options['icon']))
            ico = launcher_tool.resource_editor.icon.Icon()
            ico.load(options['icon'])
            with launcher_tool.resource_editor.ResourceEditor(launcher_temp) as res:
                ico.save_as_resource(res, 1, 1033)
        if 'python_minimal' in options:
            log.info('changing path to python-minimal to: {}'.format(options['python_minimal']))
            with launcher_tool.resource_editor.ResourceReader(launcher_temp) as res:
                string_table = res.get_string_table()
            string_table.languages[1033][1] = options['python_minimal']
            with launcher_tool.resource_editor.ResourceEditor(launcher_temp) as res:
                string_table.save_to_resource(res)
        if 'bin_dir' in options:
            log.info('changing path to python-minimal to use "bin" dir')
            with launcher_tool.resource_editor.ResourceReader(launcher_temp) as res:
                string_table = res.get_string_table()
            if self.use_python27:
                string_table.languages[1033][1] = '%SELF%/../python27-minimal'
            else:
                string_table.languages[1033][1] = '%SELF%/../python3-minimal'
            with launcher_tool.resource_editor.ResourceEditor(launcher_temp) as res:
                string_table.save_to_resource(res)
        with open(launcher_temp, 'rb') as temp_exe:
            fileobj.write(temp_exe.read())

    def write_launcher(self, filename, main_script, options):
        """\
        helper function that writes a launcher exe with the appended __main__.py
        and support files
        """
        with open(filename, 'wb') as exe:
            if 'icon' in options or 'python_minimal' in options or 'bin_dir' in options:
                self.copy_customized_launcher(exe, options)
            else:
                launcher_tool.copy_launcher.copy_launcher(exe, self.use_python27, self.is_64bits)
            with zipfile.ZipFile(exe, 'a', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('__main__.py', main_script.encode('utf-8'))
                archive.writestr('launcher.py', pkgutil.get_data('launcher_tool', 'launcher.py'))

    def process_entry_point(self, entry_point_name):
        """create a launcher for each item in the given entry point"""
        if entry_point_name in self.distribution.entry_points and self.distribution.entry_points[entry_point_name]:
            #~ print(self.distribution.entry_points[entry_point_name])
            for combination in self.distribution.entry_points[entry_point_name]:
                name, entry_point = combination.split('=')
                name = name.strip()
                entry_point = entry_point.strip()
                exe_name = '{}.exe'.format(name)
                options = self.get_option_dict_for_file(exe_name)
                if 'bin_dir' in options:
                    self.mkpath(os.path.join(self.dest_dir, 'bin'))
                    filename = os.path.join(self.dest_dir, 'bin', exe_name)
                else:
                    filename = os.path.join(self.dest_dir, exe_name)
                main_script = launcher_tool.launcher_zip.make_main(
                    entry_point=entry_point,
                    extend_sys_path=self.extend_sys_path_list,
                    wait_at_exit=options.get('wait_at_exit', False),
                    wait_on_error=options.get('wait_on_error', False),
                    use_bin_dir=options.get('bin_dir', False))
                self.execute(self.write_launcher,
                             (filename, main_script, options),
                             'writing launcher {}'.format(filename))

    def process_scripts(self):
        """create a launcher for each item in the 'scripts' list"""
        for source in self.distribution.scripts:
            exe_name = '{}.exe'.format(os.path.basename(source))
            options = self.get_option_dict_for_file(exe_name)
            if 'bin_dir' in options:
                self.mkpath(os.path.join(self.dest_dir, 'bin'))
                filename = os.path.join(self.dest_dir, 'bin', exe_name)
            else:
                filename = os.path.join(self.dest_dir, exe_name)

            script = open(source).read()
            # append users' script to the launcher boot code
            main_script = '{}\n{}'.format(
                launcher_tool.launcher_zip.make_main(
                    extend_sys_path=self.extend_sys_path_list,
                    wait_at_exit=options.get('wait_at_exit', False),
                    wait_on_error=options.get('wait_on_error', False),
                    use_bin_dir=options.get('bin_dir', False)),
                script)
            self.execute(self.write_launcher,
                         (filename, main_script, options),
                         'writing launcher {}'.format(filename))

    def run(self):
        #~ print(dir(self.distribution))
        #~ print(self.distribution.scripts)
        #~ print(self.distribution.requires)

        log.info('installing to {}'.format(self.dest_dir))
        self.mkpath(self.dest_dir)

        log.info('preparing a wheel file of application')
        self.run_command('bdist_wheel')
        log.info('installing wheel of application (with dependencies)')
        self.spawn([sys.executable, '-m', 'pip', 'install',
                    '--disable-pip-version-check',
                    '--prefix', self.dest_dir,
                    '--ignore-installed',  # '--no-index',
                    '--find-links=dist', self.distribution.get_name()])

        if hasattr(self.distribution, 'entry_points') and self.distribution.entry_points:
            self.process_entry_point('console_scripts')
            self.process_entry_point('gui_scripts')

        if hasattr(self.distribution, 'scripts') and self.distribution.scripts:
            self.process_scripts()

        if self.python_minimal is None:
            if self.use_python27:
                if not os.path.exists(os.path.join(self.dest_dir, 'python27-minimal')):
                    launcher_tool.create_python27_minimal.copy_python(
                        os.path.join(self.dest_dir, 'python27-minimal'))
                else:
                    log.info('python27-minimal installation already present')
            else:
                if not os.path.exists(os.path.join(self.dest_dir, 'python3-minimal')):
                    log.info('extracting python minimal installation')
                    launcher_tool.download_python3_minimal.extract(
                        launcher_tool.download_python3_minimal.get_url(
                            '{0.major}.{0.minor}.{0.micro}'.format(sys.version_info),
                            64 if self.is_64bits else 32),
                        os.path.join(self.dest_dir, 'python3-minimal'))
                else:
                    log.info('python3-minimal installation already present')
