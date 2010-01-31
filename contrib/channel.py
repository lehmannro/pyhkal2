
__requires__('irc')

hi (
    version = "0.0a",
)

tube_getter = chaos('channels.channels', 'if(doc.type=="channel") emit')
shit_getter = chaos('channels.nicks')

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
    dispatch_event('irc.send', 'WHO %s %%na' % tname)

@hook('irc.kicked')
def remove_tube(tname):
    del tubes[tname]

@hook('irc.isupport')
def get_chan_modes(*_, **__):
    global chan_mode_chars
    chan_mode_chars = irc.options['CHANMODES'].split('=')

    
    

@hook('irc.setmode')
def set_mode(tname, user, set, mode, args):
    args = list(args)
    tube = chaos()
    

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
        shits = shit_getter()
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



