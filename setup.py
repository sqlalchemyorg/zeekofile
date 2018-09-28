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
]

setup(
    name="zeekofile",
    version=zeekofile.__version__,
    description="A static website compiler",
    long_description=long_description,
    author="Ryan McGuire and Mike Bayer",
    url="http://bitbucket.org/zzzeek/zeekofile",
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3'
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: Implementation :: CPython',
        'Environment :: Console',
        'Natural Language :: English',
    ],
    packages=["zeekofile"],
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': ['zeekofile = zeekofile.main:main']},
)
