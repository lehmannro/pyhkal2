from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.python import usage
from pyhkal.screwdriver import Screwdriver
from pyhkal.engine import Pyhkal

class PyhkalOptions(usage.Options):
    def parseArgs(self, *args):
        if len(args) == 1:
            self.config, = args
        else:
            self.opt_help()
    def getSynopsis(self):
        return "usage: twisted [options] pyhkal <config.yaml>"

class PyhkalServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = 'pyhkal'
    description = "An IRC bot with bling bling!"
    options = PyhkalOptions

    def makeService(self, options):
        screwdriver = Screwdriver(options.config)
        return Pyhkal(screwdriver)
