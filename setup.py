#!/usr/bin/env python

from distutils.core import setup
#import pyhkal

setup(name='pyhkal',
#      version=pyhkal.__version__,
#      description="",
#      long_description="",
      url="http://github.com/lehmannro/pyhkal/",
#      author="",
#      author_email="",
#      license="",
      packages=['pyhkal', 'pyhkal.contrib', 'pyhkal.test'],
      package_dir={'pyhkal.contrib': 'contrib', 'pyhkal.test': 'test'},
      package_data={'pyhkal': ['service.tac']},
      scripts=['bin/pyhkal-configure'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Topic :: Communications :: Chat :: Internet Relay Chat',
      ],
)
