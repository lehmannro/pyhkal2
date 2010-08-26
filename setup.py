#!/usr/bin/env python

from distutils.core import setup
#from setuptools import setup
#import pyhkal

setup(name='pyhkal',
#      version=pyhkal.__version__,
#      description="",
#      long_description="",
      url="http://github.com/lehmannro/pyhkal2/",
#      author="",
#      author_email="",
#      license="",
      packages=['pyhkal', 'pyhkal.contrib', 'pyhkal.test', 'twisted.plugins'],
      package_dir={'pyhkal.contrib': 'contrib', 'pyhkal.test': 'test'},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Topic :: Communications :: Chat :: Internet Relay Chat',
      ],
)
