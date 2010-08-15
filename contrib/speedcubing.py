"""

    Der fabuloese SpeedcubingMod

"""

from twisted.internet import defer
import time
from math import floor

__version__ = "0.1a"
__requires__ = ["irc"]

@hook("message",expr="^(\*cube)?.*")
def startCubeTimer(event,r):
    if not hasattr(event.source, "cube") or event.source.cube == None and event.content.split()[0] == "*cube":
        event.source.cube = time.time()
    else:
        if hasattr(event.source, "cube") and not event.source.cube == None:
            needed = floor((time.time() - event.source.cube)*100)/100
            event.reply("%s: %.2f" % (event.source.nick, needed))
            event.source.cube = None
