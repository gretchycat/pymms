#!/usr/bin/python3
from setuptools import setup, find_packages
import shutil

with open('README.md') as f:
    long_description = f.read()
shutil.copyfile('gm_pymms/termplayer.py', 'gm_pymms/pymms')

setup(
    name='gm_pymms',
    version='0.0.1',
    license='GPL3',
    url='https://github.com/gretchycat/pymms',
    author='Gretchen Maculo',
    author_email='gretchen.maculo@gmail.com',
    description='python xmms inspired media player/recorder',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'pydub',
        'gm_termcontrol'
    ],
    tests_require=[
    ],
    scripts=['gm_pymms/pymms']
)
