#!/usr/bin/python3


from setuptools import setup

setup(
    name='org_wayround_xmpp',
    version='0.7.3',
    description='XMPP protocol implementation',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/org_wayround_xmpp',
    packages=[
        'org.wayround.xmpp'
        ],
    install_requires=[
        'org_wayround_utils',
        'org_wayround_gsasl'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ]
    )
