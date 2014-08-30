#!/usr/bin/python3

import os.path

from setuptools import setup

setup(
    name='org_wayround_xmpp',
    version='0.7',
    description='XMPP protocol implimentation',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/org_wayround_xmpp',
    packages=[
        'org.wayround.xmpp'
        ],
    install_requires = ['org_wayround_utils']
    )
