#!/usr/bin/env python

"""
"""

import os.path
import yaml

_cache = None

def read(sheet):
    global _cache
    _cache = yaml.safe_load(file(os.path.normpath(sheet)))

def remember(breadcrumbs):
    """Remember that random fact that popped into your head 2 AM in the
    morning.

    You should probably `read` your notes beforehand.

    """
    global _cache
    return reduce(lambda doc, value: doc[value], breadcrumbs.split(), _cache)

