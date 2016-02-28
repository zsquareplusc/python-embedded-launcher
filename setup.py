# setup.py for python-embedded-launcher
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import subprocess
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# compile the launcher binaries
# other users may need to edit the batch file or add gcc somehow to the PATH
print subprocess.check_output(['compile_all.bat'], cwd='src', shell=True)

setup(
    name="python-embedded-launcher",
    description="Python Embedded Launcher",
    version='0.1',
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="https://github.com/zsquareplusc/python-embedded-launcher",
    packages=['launcher_tool'],
    package_data={'launcher_tool': ['launcher27.exe', 'launcher3.exe']},
    license="BSD",
    long_description="Launcher exe for distributin Python apps on Windows",
    classifiers=[
        #~ 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],
    platforms='any',
)
