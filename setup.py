#!/usr/bin/env python
# -*- coding:utf-8 -*-
from distutils.core import setup
import py2exe

setup(
    console=['corona-archiver.py'],
    name='CoronaArchiver',
    version='1.0',
    description='Corona archive file packer/unpacker',
    author='0BuRner',
    url='https://github.com/0BuRner/corona-archiver'
)
