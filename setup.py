#!/usr/bin/env python

"""Setup file for pslocate."""

from distutils.core import setup

setup(
    name='perfsonar-pslocate',
    version='1.0',
    description='Tools for finding perfSONAR measurement points along a path',
    author='Andy Lake',
    author_email='andy@es.net',
    url='http://www.perfsonar.net',
    packages=['pslocate'],
    scripts=['bin/pslocate'],
    #data_files=[('/etc/perfsonar', ['conf/pslocate.conf' ])],
    install_requires=[
        'elasticsearch>=2.3.0', 'jsonschema>=2.5.1', 'flask>=0.10.1'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'Environment :: Console',
        'License :: OSI Approved :: Apache License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: Software Development :: Libraries',
    ],
)