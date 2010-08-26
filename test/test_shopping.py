from pyhkal.test.support import TestCase
from pyhkal import shopping

class ReloadingTest(TestCase):
    def test_reload(self):
        shopping.buy('irc')
        callbacks = sum(len(hooks) for hooks in
                self.service.listeners.itervalues())
        shopping.renew('irc')
        callbacks_again = sum(len(hooks) for hooks in
                self.service.listeners.itervalues())
        self.assertEquals(callbacks, callbacks_again,
            "new callbacks should have replaces old ones")
