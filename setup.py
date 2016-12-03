#!/usr/bin/python3


from setuptools import setup

setup(
    name='wayround_i2p_xmpp',
    version='0.8.1',
    description='XMPP protocol implementation',
    author='Alexey V Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_i2p_xmpp',
    packages=[
        'wayround_i2p.xmpp'
        ],
    install_requires=[
        'wayround_i2p_utils',
        'wayround_i2p_gsasl'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ]
    )
