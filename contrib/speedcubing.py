"""

    Der fabuloese SpeedcubingMod

"""

__version__ = "0.3"

from random import choice

def cubescramble(num):
    MOVES = [["U", "D"], ["R", "L"], ["F", "B"]]
    MOVEMODS = ["", "", "2", "'"] # no prefix is twice as likely
    scramble = []
    for x in xrange(num):
        d = {}

        axes = range(3)
        # axis came two times in a row, enough is enough
        if len(scramble) > 1 and scramble[-2]['axis'] == scramble[-1]['axis']:
            axes.remove(scramble[-1]['axis'])
        d['axis'] = choice(axes)

        moves = range(2)
        # same axis as last time, don't make the same move
        if len(scramble) > 0 and d['axis'] == scramble[-1]['axis']:
            moves.remove(scramble[-1]['move'])
        d['move'] = choice(moves)

        d['movemod'] = choice(range(len(MOVEMODS)))
        scramble.append(d)
    return " ".join(MOVES[d['axis']][d['move']] + MOVEMODS[d['movemod']] for d in scramble)

@register("3")
def getCubeScramble(event):
    event.reply("Try %s" % cubescramble(25))

@hook("message", expr=r'^\*cube\b')
def startCubeTimer(event, r):
    if not hasattr(event.source, 'cube'):
        # source will persist through events
        event.source.cube = event.timestamp

@hook("message")
def stopCubeTimer(event):
    if hasattr(event.source, 'cube') and not event.content.startswith('*cube'):
            timed = event.timestamp - event.source.cube
            assert timed >= 0, "bogus timestamp information or major logic flaw"
            # can timed be zero, actually?
            event.reply("%s: %s" % (event.source.nick, timed))
            del event.source.cube
