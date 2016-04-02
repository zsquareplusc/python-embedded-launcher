#!python
"""\
setup.py for sample application.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="sample_application",
    description="Small sample application for python-embedded-launcher",
    version='0.1',
    packages=['app'],
    platforms='any',
)
