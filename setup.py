# -*- coding: utf-8 -*-
from setuptools import setup
import zeekofile


with open('README.rst', 'rt') as readme:
    long_description = readme.read()

install_requires = [
    'docutils',
    'Mako',
    'Markdown',
    'MarkupSafe',
    'Pygments',
    'pytz',
    'PyYAML',
    'six',
]
dependency_links = []

classifiers = [
    'Programming Language :: Python :: {0}'.format(py_version)
    for py_version in ['2.7', '3']]
classifiers.extend([
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: Implementation :: CPython',
    'Environment :: Console',
    'Natural Language :: English',
])

setup(
    name="zeekofile",
    version=zeekofile.__version__,
    description="A static website compiler",
    long_description=long_description,
    author="Ryan McGuire and Mike Bayer",
    url="http://bitbucket.org/zzzeek/zeekofile",
    license="MIT",
    classifiers=classifiers,
    packages=["zeekofile"],
    install_requires=install_requires,
    dependency_links=dependency_links,
    zip_safe=False,
    entry_points={
        'console_scripts': ['zeekofile = zeekofile.main:main']},
)
