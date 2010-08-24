"""

    Der fabuloese SpeedcubingMod

"""

import time #XXX consult event.time instead of time.time

__version__ = "0.2"

@hook("message", expr=r'^\*cube\b')
def startCubeTimer(event, r):
    if not hasattr(event.source, 'cube'):
        event.source.cube = (time.time(), event)

@hook("message")
def stopCubeTimer(event):
    if hasattr(event.source, 'cube'):
        starting_time, trigger_event = event.source.cube
        if event != trigger_event:
            timed = time.time() - starting_time 
            event.reply("%s: %.2g" % (event.source.nick, timed))
            del event.source.cube
