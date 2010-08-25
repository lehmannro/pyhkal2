"""

    Der fabuloese SpeedcubingMod

"""

__version__ = "0.3"

@hook("message", expr=r'^\*cube\b')
def startCubeTimer(event, r):
    if not hasattr(event.source, 'cube'):
        # source will persist through events
        event.source.cube = event.timestamp

@hook("message")
def stopCubeTimer(event):
    if hasattr(event.source, 'cube') and not event.content.startswith('*cube'):
            timed = event.timestamp - event.source.cube
            assert timed > 0, "bogus timestamp information or major logic flaw"
            event.reply("%s: %s" % (event.source.nick, timed))
            del event.source.cube
