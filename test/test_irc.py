from pyhkal.test.support import TestCase

class IrcUserTest(TestCase):
    modules = ['irc']

    def test_constructor(self):
        self.assertRaises(AttributeError, self.irc.IRCUser)
        # requires at least nick
        u = self.irc.IRCUser(nick="foobar")
        self.assertEqual(u.nick, "foobar")

class WhoTest(TestCase):
    modules = ['irc']

    def test_simple(self):
        client = self.irc.IRCClientFactory().buildProtocol(0)
        d = client.getInfo("person")
        #XXX get the WHO id
        # Emulate the server.
        client.lineReceived(":mock.server 354 PyHKAL 1 "
            "~person person.hostmask person H 0 :Some Person")
        client.lineReceived(":mock.server 315 PyHKAL #location")

        @d.addCallback
        def assertion(value):
            self.assertEquals(value[0]['ident'], "~person")
            self.assertEquals(value[0]['host'], "person.hostmask")
            self.assertEquals(value[0]['nick'], "person")
            self.assertEquals(value[0]['flags'], "H")
            self.assertEquals(value[0]['auth'], None) # 0
            self.assertEquals(value[0]['realname'], "Some Person")
            self.assertEquals(value[0]['away'], False)

        return d
