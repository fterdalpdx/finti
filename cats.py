'''
Created on Feb 1, 2015

@author: dennis
'''
import random

cats = [
    ";;;=`v`=```",
    "=^..^=",
    "='^'=",
    "=^.^=",
    ">'o'<",
    ",,,^..^,,,~",
    ">'.'<",
    "=^_^=",
    "(=^'I'^=)",
    "V(=^'w'^=)V",
    "(=`w'=)",
    "o(^'x'^)o",
    "(^._.^)/",
    "~(=^..^)/",
    "^..^",
    ]

def here_kitty():
    pounce = random.randint(0, len(cats) - 1)
    return cats[pounce]
