"""
  UserMod made of awesome
  
  - Funktion zum ein-/ausloggen
  - Ausloggen wenn:
    - Kein Comchannel mehr besteht
    - LogOut-Funktion
  - Beobachten von Nickchanges
  
  
  DB Struktur
  - Accountname
  - Passwort
  - Server-Authname
  - LoggedIn-Nick
  - mod-einstellungen als Unterbaum
  
  {
    "type": "user",
    "accountname": "Janno",
    "loggedinas": "jannotb",
    "lastactivity": "1264931913.209357",
    "qauth": "janno",
    "tikkle": {
        "login": "ich.bin.nur.der(.*).koch",
        "afk": "(.*)afk(.*)",
        "logout": "bye"
    }
  }
"""

__version__ = "0.1a"
__requires__ = ['irc',"channel"]


viewAccount = chaos("UserAccount",
    """
        if (doc.type == "user") {
            emit(doc.accountname,doc)
        }
    """)

viewAccountByOrigin = chaos("UserAccountByOrigin",
    """
        if (doc.type == "user") {
            emit(doc.loggedinas,doc)
        }
    """)

@register("login")
def login_cmd(origin, args):
    if (args == []):
        self.identify(origin)
    else:
        account = self.getAccountByOrigin(origin)
        self.login(origin, args[0], ' '.join(args[1:]))

@register("logout")
def logout_cmd(origin, args):
    self.logout(origin)

def identify(origin):
    """
      Tries to identify the user without him having to log in using a password.
    """
    serverauth = self.getServerAuthByOrigin(origin)
    account = self.getAccountByOrigin(origin)
    if (serverauth and self.isLoggedIn(account) == False):
        self.logout(origin)
        self.setInfo(account, "loggedinas", self.getInfo(account, "loggedinas").append(origin))
        dispatch_event("user.loggedin", name) # >> 4

def login(origin, name, password):
    account = self.getAccountByOrigin(origin)
    if (getInfo(account, "password") == self.hashPass(name, password)):
        self.logout(origin)
        self.setInfo(account, "loggedinas", self.getInfo(account, "loggedinas").append(origin))
        dispatch_event("user.loggedin", name)
        irc.send("Logged in.")
    else:
        irc.send("Login failed")

def logout(account):
    if (isLoggedIn(account)):
        self.setInfo(account, "loggedinas", self.getInfo(account, "loggedinas").remove(origin))
        dispatch_event("user.loggedout", name)

def adduser():
    """"""

def getAccountByOrigin(origin):
    if (isLoggedIn(origin)):
        account = viewAccount()[origin]["accountname"]
        return account

def getServerAuthByOrigin(origin):
    return channel.isAuthed(origin.nick)

def isLoggedIn(origin):
    account = self.getAccountByOrigin(origin)
    return (origin in self.getInfo(account, "loggedinas"))

def setLastActivity(account):
    import time
    setInfo(account, "lastactivity", time.time())

def hashPass(password):
    import hashlib
    h = hashlib.new('sha256')
    h.update(name + password) #TODO salty pirate arr
    return h.hexdigest()

# Penis Penis Penis! Macht das Davenport Zeug
def getInfo(account, data):
    return viewAccount()[account][data]

def setInfo(account, data, value):
    if (data == "password"): value = hashPass(value)
    viewAccount()[account][data] = value
