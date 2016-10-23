#!/usr/bin/env python
import os
import sys

from setuptools import setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

with open(os.path.join(SOURCE_DIR, 'requirements.txt'), 'r') as f:
    requirements = f.read().splitlines()

setup(
    name="libcet",
    version='0.2',
    description="Reverse from 99sushe.",
    url='https://github.com/realityone/libcet',
    packages=['libcet'],
    install_requires=requirements,
    zip_safe=False, )
