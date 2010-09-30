#!/usr/bin/env python

from setuptools import setup
#import pyhkal

setup(name='PyHKAL',
#      version=pyhkal.__version__,
      description="IRC bot with bling bling",
#      long_description="",
      url="http://github.com/lehmannro/pyhkal2/",
#      author="",
#      author_email="",
#      license="",
      packages=['pyhkal', 'pyhkal.contrib', 'pyhkal.test'],
      package_dir={'pyhkal.contrib': 'contrib', 'pyhkal.test': 'test'},
      install_requires=[
          'twisted',
          'paisley',
          'pyopenssl',
          'oauth',
          'twittytwister',
          'PyYAML',
        ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Topic :: Communications :: Chat :: Internet Relay Chat',
      ],
)
