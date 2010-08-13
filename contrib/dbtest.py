#!/usr/bin/env python

__requires__ = []

chaos('dbtest', 'emit(doc, null);')

def blafu(*args):
    for arg in args:
        print arg

davenport.openView('dbtest', 'dbtest').addBoth(blafu)
