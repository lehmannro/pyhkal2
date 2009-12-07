hi(
    name = "user",
    version = "0.1beta",
    desc = "user management",
)

admin_list = [User("StruC")]
admins = [Origin("query", "StruC"), Origin("query", "starGaming")]
admins = [Origin("channel", "&partyline")]

class User(object):
    def __init__(self, transports):
        self.transports = transports
    def contact(self, message):
        for t in self.transports:
            if heuristik(t): #+ Prioritäten?
                t(message)