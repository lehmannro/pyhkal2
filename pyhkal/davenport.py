#!/usr/bin/env python

"""Document storage for PyHKAL

"""

import couchdb

def get(*args):
    return database.get(*args)

def put(path, obj):
    database.put(path, obj)

