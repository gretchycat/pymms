#!/usr/bin/python3
from setuptools import setup, find_packages
import shutil

with open('README.md') as f:
    long_description = f.read()
shutil.copyfile('pymms/termplayer.py', 'pymms/pymms')

setup(
    name='pymms',
    version='0.0.1',
    license='GPL3',
    url='https://github.com/gretchycat/pymms',
    author='Gretchen Maculo',
    author_email='gretchen.maculo@gmail.com',
    description='python xmms inspired media player/recorder',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['pymms'],
    install_requires=[
        'pydub',
        'pyte',
    ],
    tests_require=[
    ],
    scripts=['pymms/pymms']
)
