class IRCUser(Avatar):
    def __init__(self, nick, hmask):
        self.nick = nick
        self.hmask = hmask

    def message(self, target, text):
        dispatch_event("irc.sendmessage", target, text)
