#!/usr/bin/env python

"""
Document storage.

"""

import paisley
from base64 import b64encode

class Davenport(paisley.CouchDB):
    def __init__(self, host, db, user, passwd, port=5984):
        paisley.CouchDB.__init__(self, host, port, dbName=db)
        self.auth = "Basic %s:%s" % (user, passwd)

    def _getPage(self, uri, **kwargs):
        headers = kwargs.setdefault('headers', {})
        headers['Authorization'] = self.auth
        return paisley.CouchDB._getPage(self, uri, **kwargs)

    def order(self, module, by, map_fun, reduce_fun=None):
        #XXX reduce_fun
#        "function(keys, values){ %s }" % reduce_fun if reduce_fun else None
        payload = "function(doc){ %s }" % map_fun
        docname = '_design/%s' % module
        def add_view(doc):
            if isinstance(doc, Exception):
                doc = {}
            self.addViews(doc, {by: payload})
            self.saveDoc(doc)
        self.openDoc(docname).addBoth(add_view)
