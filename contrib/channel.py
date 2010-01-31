
__requires__ = ['irc']

__version__ = "0.0a"

tube_getter = chaos('channels.channels', 'if(doc.type=="channel") emit(doc.name, doc);')
shit_getter = chaos('channels.nicks', 'if(doc.type=="nick") emit(doc.name, doc);')
shit_by_tube_getter = chaos('channels.nicks_by_tube', 'if(doc.type=="nick") { for channel in doc.channels { emit(channel, doc);  } } ')

names_done = {}

def get_tube(tname):
    chaos('channel', '')

def put_doc(doc):
    pass

def flush_tubes():
    put_data_by_label(SEWERS, tubes)

@hook('irc.joined')
def add_tube(tname):
    put_doc({'type': 'channel', 'name': name})
    names_done[tname] = True

@hook('irc.kicked')
def remove_tube(tname):
    del tubes[tname]


@hook('irc.setmode')
def set_mode(tname, user, set, modes, args):
    args = list(args)
    tube = tube_getter()[tname]
    while modes:
        mode = mode.pop()
        if not (mode in irc.chanmodes['noParam']):
            tube['modes']['mode'] = args.pop()
    order(tube)

@hook('irc.delmode')
def set_mode(tname, user, set, modes, args):
    args = list(args)
    tube = tube_getter()[tname]
    while modes:
        mode = mode.pop()
        if not ((mode in irc.chanmodes['noParam']) or (mode in irc.chanmodes['setParam'])):
            tube['modes']['mode'] = args.pop()
    order(tube)



def get_modes_by_shit(shit):
    mode_chars = ['@', '+', '%']
    modes = []
    while shit and shit[0]:
        modes.append(shit[0])
        shit = shit[1:]
    return modes


@hook('irc.names')
def add_names(tname, names):
    if names_done:
        names_done[tname] = False
        for name in shits_by_tube(tname):
            remove_shit_from_tube(tname, shit)
    for name in names:
        modes = get_modes_by_shit(name)
        shits = shit_getter()[name]
        if name in shits:
            shit = shits[name]
        else:
            shit = {'type': 'nick','nick': name, 'channels': {}}
        shit['channels'][tname] = {'modes': modes}
        order(shit)
        
        
@hook('irc.endofnames')
def end_names(tname):
    names_done[tname] = True

@hook('irc.whoreply')
def who_reply(resultdict):
    pass 

def get_auth_nick(nick, callback):
    callback('Janno') 



