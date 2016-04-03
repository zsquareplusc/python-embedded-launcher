#!python
"""\
setup.py for sample application.
"""
from setuptools import setup

setup(
    # cmdclass = {'bdist_launcher':launcher_tool.bdist_launcher:bdist_launcher}, # XXX for distutils

    name="sample_application",
    description="Small sample application for python-embedded-launcher",
    version='0.1',
    packages=['app'],
    platforms='any',
    install_requires=[
        'pyserial >= 3',
    ],
    entry_points={
        'console_scripts': [
            'app = app.core:main',
            'ports = serial.tools.list_ports:main',
        ],
    },
    scripts=['scripts/mt'],
)
