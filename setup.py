#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup

setup(
    name='entities',
    version='1.0.0',
    author='Eser Aygün',
    author_email='eser.aygun@gmail.com',
    packages=['entities'],
    url='https://github.com/eseraygun/python-entities',
    license='LICENSE.txt',
    description=
        'Python library for automatic object validation and serialization.',
    long_description=open('README.rst').read(),
    requires=['pytz'],
)
