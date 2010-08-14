#!/usr/bin/env python

__requires__ = ['irc']

import re
from time import strftime

def asciicount(text):
    return sum(map(ord, text))

DECIDERE = re.compile(r'(".+?"|(?<!").+?(?!"))(?:\s+|$)') 

@hook('privmsg', expr='!decide')
def handler(event):
    args = event.content.split(' ', 1)[1]
    num = asciicount("*!*" + event.source.ident)
    decide_result = regexdecide(args, num)    
    event.reply('Du solltest dich %s entscheiden' % decide_result)
    
    

def regexdecide(text, num):
    matchlist = sorted(DECIDERE.findall(text))
    c = asciicount(text) + asciicount(strftime("%d/%m/%Y"))
    if len(matchlist) > 1:
        return "für " + matchlist[(c + (num % 100)) % len(matchlist)]
    else:
        if ((c % (num % 100)) % 2 + 1) == 1:
            return "dafür"
        else:
            return "dagegen"
