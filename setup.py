#!/usr/bin/python3


from setuptools import setup

setup(
    name='wayround_org_xmpp',
    version='0.8.1',
    description='XMPP protocol implementation',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_org_xmpp',
    packages=[
        'wayround_org.xmpp'
        ],
    install_requires=[
        'wayround_org_utils',
        'wayround_org_gsasl'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ]
    )
