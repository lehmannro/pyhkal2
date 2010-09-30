"""
    Der faluboese BlackjackMod
"""

from random import randrange
from twisted.internet.task import deferLater
import datetime
from twisted.internet import reactor
from random import randrange
from itertools import combinations


__version__ = "0.%s" % randrange(21)

# Minimal number of players
# required to start the game
MIN_PLAYERS = remember('blackjack min_players', 2) 

# seconds before the game starts
# if no player joined or left
# during that time and MIN_PLAYERS
# is satisfied
WAIT_FOR = remember('blackjack wait_for', 10) 

assert WAIT_FOR < 60*60*24, 'Due to datetime.timedelta\'s incompetence and maybe just a little bit of lazyness on my part, this has to be enforced.'

wait_for_td = datetime.timedelta(0, WAIT_FOR)

# Number of decks to be used
DECKS = remember('blackjack decks', 6)

# remind everyone to join every
# REMIND_PERIOD seconds if REMIND
# is True
REMIND = remember('blackjack reminder remind', True)
REMIND_PERIOD = remember('blackjack reminder period', 5)

# wait TIMEOUT seconds before
# assuming that players who
# have not yet used "stand",
# "hit", etc. are implying "stand"
TIMEOUT = remember('blackjack timeout', 20)


class Player(object):
    def __init__(self, avatar, hand=None):
        self.avatar = avatar
        if hand:
            self.hand = hand
        else:
            self.hand = Hand()
    def calcPoints(self):
        return self.hand.calcPoints()
    def getName(self):
        return self.avatar.nick

class Dealer(object):
    def __init__(self, hand=None):
        if hand:
            self.hand = hand
        else:
            self.hand = DealerHand()
    def calcPoints(self):
        return self.hand.calcPoints()
    def getName(self):
        return 'Dealer' 

class Hand(object):
    def __init__(self, cards=[]):
        self.cards = cards
    def calcTrivial(self):
        result = 0
        aces = filter(lambda x: x == 'A', self.cards)
        rest = filter(lambda x: x != 'A', self.cards)
        result += sum(map(CARDS.get, rest))
        return result, aces

    def __str__(self):
        return ', '.join(self.cards)

    def calcPoints(self):
        result, aces = self.calcTrivial()
        comb = list(set(combinations([1,11]*len(aces), len(aces))))
        comb.sort(cmp=lambda x,y: cmp(sum(x), sum(y)))
        gte21 = filter(lambda x: sum(x) + result <= 21, comb)
        if gte21:
            # add highest combination of counting aces as
            # either 11 or 1 that does not end in a bust
            result += sum(gte21[-1])
        else:
            # if there is no such combination, add the
            # lowest combination
            result += sum(comb[0])

        return result


class DealerHand(Hand):
    def __init__(self, cards=[]):
        Hand.__init__(self, cards)
    
    def calcPoints(self):
        result, aces = self.calcTrivial()
        for ace in aces:
            if result + 11 <= 21:
                result += 11
            else:
                result += 1
        return result


CARDS = {
        '2':2,
        '3':3,
        '4':4,
        '5':5,
        '6':6,
        '7':7,
        '8':8,
        '9':9,
        '10':10,
        'J':10,
        'Q':10,
        'K':10,
        'A':11,
        }


jobs = ['reminder', 'starter', 'next']


def init(bj):
    bj_default = {
                'status': 'new',
                'players': {}, 
                'dealer': None,
                'rdy_players': [],
                'standing': [],
                'last_activity': None, # start in last_activity + WAIT_FOR seconds
                'reminder': None,
                'starter': None,
                'next': None,
                'deck': [], 
                }
    bj.update(bj_default) 
    bj['last_activity'] = datetime.datetime.now()

    pool = CARDS.keys() * DECKS

    while pool:
        bj['deck'].append(pool.pop(randrange(len(pool))))



def start(target):
    bj = target.blackjack
    scheduled_start = bj['last_activity'] + wait_for_td
    now = datetime.datetime.now()

    if len(bj['players']) < MIN_PLAYERS:
        bj['starter'] = reactor.callLater((scheduled_start - now).seconds, start, target)
    elif (scheduled_start <= now) or (len(bj['rdy_players']) == len(bj['players'])):
        bj['status'] = 'running'
        if bj['reminder'] and bj['reminder'].active():
            bj['reminder'].cancel()
        target.message('It\'s time for blackjack!')
        initial_deal(target)
    else:
        bj['starter'] = reactor.callLater((scheduled_start - now).seconds, start, target)

        
def initial_deal(target):
    bj = target.blackjack

    # misc

    # deal to self
    c1 = bj['deck'].pop()
    bj['dealer'] = Dealer(DealerHand([c1]))
    #target.message('Dealer draws: %s' % c1)

    # deal to players
    for avatar, player  in bj['players'].iteritems():
        c1 = bj['deck'].pop()
        c2 = bj['deck'].pop()
        player.hand.cards = [c1, c2]
        player.avatar.message('Your hand: %s (%s). Use "!bj stand" to stand pass or "!bj hit" to request another card.' % (player.hand, player.calcPoints()))


    bj['next'] = reactor.callLater(TIMEOUT, stop, target)


def stop(target):
    target.message('Time\'s up or everbody\'s busted. Let\'s see what he have here..')
    bj = target.blackjack

    dealer = bj['dealer']

    while dealer.calcPoints() < 17:
        card = bj['deck'].pop()
        dealer.hand.cards.append(card)
        if dealer.calcPoints() > 21:
            #target.message('The dealer is busted.')
            break

    all_players = bj['players'].values()
    all_players.append(dealer)
    busted = filter(lambda p: p.calcPoints() > 21, all_players)
    valid = filter(lambda p: p.calcPoints() <= 21, all_players)
    valid.sort(lambda x,y: cmp(y.calcPoints(), x.calcPoints()))
    busted.sort(lambda x,y: cmp(y.calcPoints(), x.calcPoints()))

    if valid:
        highest = valid[0].calcPoints()
        for player in valid: 
            target.message('%s: %s (%s) [%s]' % (player.getName(), player.calcPoints(), player.hand, 'Winner' if player.calcPoints() == highest else 'Loser'))
    if busted:
        target.message('Busted: %s' % ', '.join(['%s: %s (%s) [Loser]' % (player.getName(), player.calcPoints(), player.hand) for player in busted]))

    bj['status'] = 'over'


def remind(target):
    bj = target.blackjack
    if bj['status'] == 'new':
        scheduled_start = bj['last_activity'] + wait_for_td
        now = datetime.datetime.now()
        diff = scheduled_start - now
        num_players = len(bj['players'])
        if num_players >= MIN_PLAYERS:
            target.message('This game of blackjack is set to start in %s seconds. %s player%s currently in the game. Join by saying "!blackjack"!' % (diff.seconds, num_players, ' is' if num_players == 1 else 's are'))
        else:
            target.message('This game of blackjack does not have enough players. %s of %s required players have joined already. Join by saying "!blackjack"!' % (num_players, MIN_PLAYERS))

    bj['reminder'] = reactor.callLater(REMIND_PERIOD, remind, target)


@register('bj')
@register('blackjack')
def handler(event):
    args = event.content.split()
    if args:
        while args:
            if args[0] == 'leave':
                leave(event)
            elif args[0] == 'join':
                join(event)
            elif args[0] in ('ready', 'rdy'):
                rdy(event)
            elif args[0] in ('hit', 'card', 'carte', 'draw'):
                hit(event)
            elif args[0] in ('stand', 'pass'):
                stand(event)
            args.pop(0)
    else:
        join(event)

def join(event, is_rdy=False):
    if hasattr(event.target, 'blackjack') \
            and event.target.blackjack['status'] == 'new':
        bj = event.target.blackjack
        event.source.blackjack = {}
        if event.source in bj['players'].iterkeys():
            event.source.message('You are already in the game, idiot!')
        else:
            bj['players'][event.source] = Player(event.source)
            if not is_rdy:
                event.source.message('You have joined the game.')
            else:
                event.source.message('You have joined the game and voted to start the game as soon as possible.')
            bj['last_activity'] = datetime.datetime.now()
    elif hasattr(event.target, 'blackjack') \
            and event.target.blackjack['status'] == 'running':
        if event.source in event.target.blackjack['players'].iterkeys():
            event.source.message('You are already playing blackjack.')
        else:
            event.source.message('A game of blackjack is running atm. Come back soon!')
    else:
        bj = {}
        init(bj)
        event.target.blackjack = bj
        bj['players'][event.source] = Player(event.source)
        if REMIND:
            bj['reminder'] = reactor.callLater(REMIND_PERIOD, remind, event.target)
        event.reply('A new game of blackjack has been started.')
        if not is_rdy:
            event.source.message('You have joined the game.')
        else:
            event.source.message('You have joined the game and voted to start the game as soon as possible.')
        bj['last_activity'] = datetime.datetime.now()

    # event.target.blackjack must exist now
    bj = event.target.blackjack
    if len(bj['players']) >= MIN_PLAYERS:
        if bj['starter']:
            bj['starter'].reset(0)
        else:
            bj['starter'] = reactor.callLater(wait_for_td.seconds, start, event.target)

def rdy(event, is_join=False):
    if hasattr(event.target, 'blackjack'):
        bj = event.target.blackjack
        if bj['status'] == 'new':
            if event.source in bj['players'].iterkeys():
                if event.source not in bj['rdy_players']:
                    bj['rdy_players'].append(event.source)
                    if not is_join:
                        event.source.message('You have voted to start the game as soon as there are enough players.')
                    if len(bj['players']) >= MIN_PLAYERS:
                        if len(bj['rdy_players']) == len(bj['players']):
                            bj['starter'].reset(0)
            else:
                join(event, is_rdy=True)
                rdy(event, is_join=True)
        elif bj['status'] == 'over':
            join(event, is_rdy=True)
            rdy(event, is_join=True)
    else:
        join(event, is_rdy=True)
        rdy(event, is_join=True)

def stand(event):
    if hasattr(event.target, 'blackjack'):
        bj = event.target.blackjack
        if bj['status'] == 'running':
            if event.source in bj['players'].iterkeys():
                event.source.message('You stand.')
                if not event.source in bj['standing']:
                    bj['standing'].append(event.source)
                    if len(bj['standing']) == len(bj['players']):
                        bj['next'].reset(0)

def hit(event):
    if hasattr(event.target, 'blackjack'):
        bj = event.target.blackjack
        if bj['status'] == 'running':
            if event.source in bj['players'].iterkeys():
                if event.source in bj['standing']:
                    event.source.message('You decided to stand, idiot! Or you might be busted. I dunno!')
                else:
                    player = bj['players'][event.source]
                    card = bj['deck'].pop()
                    player.hand.cards.append(card)
                    event.source.message('Your hand is now %s (%s).' % (player.hand, player.calcPoints()))
                    if player.calcPoints() > 21:
                        event.source.message('You are busted!')
                        bj['standing'].append(event.source)
                        if len(bj['standing']) == len(bj['players']):
                            bj['next'].reset(0)
                    else:
                        bj['next'].reset(TIMEOUT)

def leave(event):
    if hasattr(event.target, 'blackjack'):
        bj = event.target.blackjack
        if event.source in bj['players'].iterkeys():
            del bj['players'][event.source]
            if bj['status'] == 'new':
                event.source.message('You have left the game.')

                if event.source in bj['rdy_players']:
                    bj['rdy_players'].remove(event.source)

            if bj['status'] == 'running':
                event.reply('%s leaves. What a sissy!' % event.source.nick)
                event.source.message('You have left the game.')
            if not bj['status'] == 'over':
                if len(bj['players']) == 0:
                    event.reply('All players left the game. Pussies!')
                    for job in jobs: 
                        if bj[job]:
                            if bj[job].active:
                                bj[job].cancel() 
                            bj[job] = None



