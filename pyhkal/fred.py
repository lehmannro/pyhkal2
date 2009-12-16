"""
"""

import functools
import thread

def threaded(func):
    @functools.wraps(func)
    def wrapper(*args):
        return thread.start_new_thread(func, args)
    return wrapper
