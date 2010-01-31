#!/usr/bin/env python

"""
Document storage.

One davenport oughta be enough for anybody. (This module is a singleton.)

The davenport described herein is both, a sofa and a desk.
"""

DATABASE = 'pyhkal'
REMEMBER = 'config'

import couchdb.client
import couchdb.design

_sofa = None

def use(location=None):
    """Start storing your documents in a davenport. `location` can be used to occupy a
    remote davenport. Otherwise use your local desk.

    """
    global _sofa
    server = couchdb.client.Server(location or couchdb.client.DEFAULT_BASE_URI)
    try:
        _sofa = server[DATABASE]
    except couchdb.client.ResourceNotFound:
        _sofa = server.create(DATABASE)

_none = object()
def remember(breadcrumbs, default=_none):
    """Remember that random fact that popped into your head 2 AM in the
    morning. For some weird reason, you need a sofa to remember.

    """
    config = lookup(REMEMBER)
    try:
        return reduce(lambda doc, value: doc[value],
                breadcrumbs.split(), config)
    except KeyError:
        if default is not _none:
            return default
        raise

def chaos(by, map_fun, reduce_fun=None):
    couchdb.design.ViewDocument(by, "view",
        "function(doc){ %s }" % map_fun,
        "function(keys, values){ %s }" % reduce_fun if reduce_fun else None
    )

def lookup(title):
    return _sofa[title]
