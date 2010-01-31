"""
  UserMod made of awesome
  
  - Funktion zum ein-/ausloggen
  - Ausloggen wenn:
    - Kein Comchannel mehr besteht
    - LogOut-Funktion
  - Beobachten von Nickchanges
  
  
  DB Struktur  
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

import string,random,time,hashlib
#from twisted.internet import reactor

__version__ = "0.1c"
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

#
# Login
#
@register("login")
def login_cmd(origin, args):
    if (args == []):
        self.identify(origin)
    else:
        account = self.getAccountByOrigin(origin)
        self.login(origin, args[0], ' '.join(args[1:]))

def login(origin, name, password):
    """
      Simple user:password login
      Dispatches event: user.loggedin <name>
                          or
                        user.loginfailed <name>
    """
    if (getInfo(name, "password") == self.hashPass(name, password)):
        self.logout(origin)
        self.setInfo(name, "loggedinas", self.getInfo(name, "loggedinas").append(origin))
        dispatch_event("user.loggedin", name)
    else:
        dispatch_event("user.loginfailed", name)

def identify(origin):
    """
      Tries to identify the user without him having to log in using a password.
      Dispatches event: user.loggedin <name>
    """
    serverauth = self.getServerAuthByOrigin(origin)
    account = self.getAccountByOrigin(origin)
    if (serverauth and self.isLoggedIn(account) == False):
        self.logout(origin)
        self.setInfo(account, "loggedinas", self.getInfo(account, "loggedinas").append(origin))
        dispatch_event("user.loggedin", name) # >> 4

#
# Logout
#
@register("logout")
def logout_cmd(origin, args):
    self.logout(origin)

def logout(account):
    """
      Dispatches event: user.loggedout <name>
    """
    if (isLoggedIn(account)):
        self.setInfo(account, "loggedinas", self.getInfo(account, "loggedinas").remove(origin))
        dispatch_event("user.loggedout", name)

def setLastActivity(account):
    """
      Dispatches event: user.seen <ctime>
    """
    now = time.time()
    setInfo(account, "lastactivity", now)
    dispatch_event("user.seen", now)

def setLastActivityWithTimer(account):
    """
      on activity do:
        if timer exists: nothing
        if no timer exists: create one to set "lastactivity" to time.time() in 30 minutes

      twisted reactor call later
        returns object can be cancelled
    """
    now = time.time()
    #TODO: reactor.callLater(1800, setInfo(account, "lastactivity", now))

def adduser(accountname, qauth):
    """
      Returns: a random password
      Dispatches event: user.added <accountname>
    """
    if (getInfo(accountname, "accountname")):
        dispatch_event("user.addfail", "User already exists")
        return none
    else:
        user = stash()
        user["type"] = user
        user["accoutname"] = accountname
        password = makePass()
        user["password"] = hashPass(password)
        user["qauth"] = qauth
        dispatch_event("user.added", accountname)
        return password

#
#  Helper
#
def getAccountByOrigin(origin):
    if (isLoggedIn(origin)):
        account = viewAccount()[origin]["accountname"]
        return account

def getServerAuthByOrigin(origin):
    return channel.isAuthed(origin.nick)

def isLoggedIn(origin):
    account = self.getAccountByOrigin(origin)
    return (origin in self.getInfo(account, "loggedinas"))

def hashPass(password):
    h = hashlib.new('sha256')
    h.update(name + password) #TODO salty pirate arr
    return h.hexdigest()

def makePass(minlength=8,maxlength=25):
    length=random.randint(minlength,maxlength)
    letters=string.ascii_letters+string.digits
    return ''.join([random.choice(letters) for _ in range(length)])

def getInfo(account, data):
    return viewAccount()[account][data]

def setInfo(account, data, value):
    if (data == "password"): value = hashPass(value)
    viewAccount()[account][data] = value
