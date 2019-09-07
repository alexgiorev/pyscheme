import itertools
from stypes import *

def iter_is_empty(itr):
    """Returns a pair (is-empty, equivalent-iterator)."""
    a, itr = itertools.tee(itr, 2)
    try: next(a); empty=False
    except StopIteration: empty=True
    return empty, itr

def is_list(obj):
    return type(obj) is Cons and obj.is_list or obj is nil
