"""

    Der fabuloese SpeedcubingMod

"""

import time #XXX consult event.time instead of time.time

__version__ = "0.2"

@hook("message", expr=r'^\*cube\b')
def startCubeTimer(event, r):
    if not hasattr(event.source, 'cube'):
        event.source.cube = time.time()

@hook("message")
def stopCubeTimer(event):
    if hasattr(event.source, 'cube'):
        if not event.message.startswith('*cube'):
            timed = time.time() - event.source.cube
            event.reply("%s: %.2g" % (event.source.nick, timed))
            del event.source.cube
