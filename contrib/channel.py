
__requires__ = ['irc']

__version__ = "0.0a"

channel_getter = chaos('channels.channels', 'if(doc.type=="channel") emit(doc.name, doc);')
user_getter = chaos('channels.nicks', 'if(doc.type=="nick") emit(doc.name, doc);')
#user_by_channel_getter = chaos('channels.nicks_by_channel', 'if(doc.type=="nick") { for channel in doc.channels { emit(channel, doc);  } } ')

names_done = {}

def get_channel(tname):
    chaos('channel', '')

def put_doc(doc):
    pass

def flush_channels():
    put_data_by_label(SEWERS, channels)

@hook('irc.joined')
def add_channel(tname):
    put_doc({'type': 'channel', 'name': name})
    names_done[tname] = True
    def callback(results):
        map(fill_who_info, results)
    irc.getInfo(tname, callback)

@hook('irc.kicked')
def remove_channel(tname):
    del channels[tname]


@hook('irc.setmode')
def set_mode(tname, user, set, modes, args):
    args = list(args)
    channel = channel_getter()[tname]
    while modes:
        mode = mode.pop()
        if not (mode in irc.chanmodes['noParam']): #FIXME see below
            channel['modes']['mode'] = args.pop()
    order(channel)

@hook('irc.delmode')
def set_mode(tname, user, set, modes, args): #FIXME use irc's supported.getFeature('CHANMODES') 
    args = list(args)
    channel = channel_getter()[tname]
    while modes:
        mode = mode.pop()
        if not ((mode in irc.chanmodes['noParam']) or (mode in irc.chanmodes['setParam'])):
            channel['modes']['mode'] = args.pop()
    order(channel)



def get_modes_by_user(user):
    mode_chars = ['@', '+', '%'] #FIXME use irc's supported.getFeature('PREFIX', default={'o': ('@', 0), 'v': ('+', 1)} ) 
    modes = []
    while user and user[0] in mode_chars:
        modes.append(user[0])
        user = user[1:]
    return modes, user


@hook('irc.names')
def add_names(tname, names):
    if names_done:
        names_done[tname] = False
        # handle nicks that are no longer on this channel 
    for name in names:
        modes, name = get_modes_by_user(name)
        users = user_getter[name].rows
        if users:
            user = users[0]
        else:
            user = {'type': 'nick','nick': name, 'channels': {}}
        user['channels'][tname] = {'modes': modes}
        order(user)
        
        
@hook('irc.endofnames')
def end_names(tname):
    names_done[tname] = True

@hook('irc.whoreply')
def who_reply(resultdict):
    pass 

def get_auth_nick(name, callback):
    users = user_getter[name].rows
    if len(users) == 1:
        return users[0]['authnick']
    else:
        return ''

