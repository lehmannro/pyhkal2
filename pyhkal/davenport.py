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
        kwargs['Authorization'] = self.auth
        return paisley.CouchDB._getPage(uri, **kwargs)

    _none = object()
    def remember(self, breadcrumbs, default=_none):
        """Remember that random fact that popped into your head 2 AM in the
        morning. For some weird reason, you need a sofa to remember.

        """
        config = self.lookup(REMEMBER)
        try:
            return reduce(lambda doc, value: doc[value],
                    breadcrumbs.split(), config)
        except KeyError:
            if default is not _none:
                return default
            raise

    def order(self, module, by, map_fun, reduce_fun=None):
        #XXX reduce_fun
#        "function(keys, values){ %s }" % reduce_fun if reduce_fun else None
        payload = "function(doc){ %s }" % map_fun
        return self.addViews('_design/%s' % module, (by, payload))
