#!/usr/bin/env python

"""
Document storage.

"""

from twisted.web.client import HTTPClientFactory
from twisted.python.failure import Failure
import paisley
from base64 import b64encode
from urllib import urlencode

class Davenport(paisley.CouchDB):
    def __init__(self, host, db, user, passwd, port=5984):
        paisley.CouchDB.__init__(self, host, port, dbName=db)
        self.auth = "Basic " + b64encode("%s:%s" % (user, passwd))

    def _getPage(self, uri, **kwargs):
        # paisley steals our headers so this is copypasta
        url = self.url_template % (uri,)
        kwargs["headers"] = {"Accept": "application/json",
            "Authorization": self.auth}
        factory = HTTPClientFactory(url, **kwargs)
        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred

    def order(self, module, by, map_fun, reduce_fun=None):
        #XXX reduce_fun
#        "function(keys, values){ %s }" % reduce_fun if reduce_fun else None
        payload = "function(doc){ %s }" % map_fun
        docname = '_design/%s' % module
        def add_view(doc):
            if isinstance(doc, Failure):
                doc = {}
            self.addViews(doc, {by: dict(map=payload)})
            self.saveDoc(doc, docId=docname)
        self.openDoc(docname).addBoth(add_view)

    def openView(self, dbName, docId, viewId, **kwargs):
        """
        Open a view of a document in a given database.
        """
        # paisley still queries old-style CouchDB URLs
        # old: /DBNAME/_view/DOCUMENT/VIEW
        # new: /DBNAME/_design/DOCUMENT/_view/VIEW (these work in 0.9 already)
        uri = "/%s/_design/%s/_view/%s" % (dbName, docId, viewId)
        if kwargs:
            uri += "?%s" % (urlencode(kwargs),)
        return self.get(uri
            ).addCallback(self.parseResult)
