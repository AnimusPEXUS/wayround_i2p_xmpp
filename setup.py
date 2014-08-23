#!/usr/bin/python3

import os.path

from distutils.core import setup

setup(
    name='org_wayround_xmpp',
    version='0.5',
    description='XMPP protocol implimentation',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='http://wiki.wayround.org/soft/org_wayround_xmpp',
    packages=[
        'org.wayround.xmpp'
        ]
    )
