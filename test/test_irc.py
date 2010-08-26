from pyhkal.test.support import TestCase

class IrcUserTest(TestCase):
    modules = ['irc']

    def test_constructor(self):
        self.assertRaises(AttributeError, self.irc.IRCUser)
        # requires at least nick
        u = self.irc.IRCUser(nick="foobar")
        self.assertEqual(u.nick, "foobar")
