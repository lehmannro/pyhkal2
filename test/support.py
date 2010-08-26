import twisted.trial.unittest as unittest
import sys
from pyhkal import shopping
from pyhkal import engine

class MockingPyhkal(engine.Pyhkal):
    def __init__(self):
        self.davenport = MockingDavenport()
        self.debug = False #XXX should probably be set in engine.Pyhkal
        engine.Pyhkal.__init__(self, {})

class MockingDavenport(object):
    pass

class TestCase(unittest.TestCase):
    modules = []

    def setUp(self):
        self.service = MockingPyhkal()
        self.mall = shopping.checkout(self.service)
        for module in self.modules:
            setattr(self, module, shopping.buy(module))

    def tearDown(self):
        sys.meta_path.remove(self.mall)
        for module in self.modules:
            shopping.revoke(module)
            delattr(self, module)

