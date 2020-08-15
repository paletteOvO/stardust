"""
make life easier
"""

from .pipe_fn import e
from .symbol import s
from .netutil import POST, GET, POST_json, GET_json, POST_data
from .functional import flatten
from .hash import djb2, fnv32a
from .dispatch import dispatch, predicate, refine, match
from .case import when, case, otherwise, value

Nothing = s.Nothing

def asProperty(obj, name, getter=Nothing, setter=Nothing, default=Nothing):
    """
   setter: set to default setter if setter is None
   """
    cls = obj.__class__
    propName = f"_{name}"
    if default != Nothing:
        setattr(obj, propName, default)
    if getter == Nothing:

        def _getter(self):
            return getattr(self, propName)

        getter = _getter
    if setter == Nothing:
        setattr(cls, name, property(getter))
    else:

        def _setter(self, v):
            setattr(self, propName, v)

        setattr(cls, name, property(getter, setter or _setter))


def proxyOn(self, obj):
    if "__proxyOnObj" in dir(self):
        self.__proxyOnObj.append(obj)
    else:
        if "proxying" not in dir(self.__class__):
            proxying(self.__class__)
        setattr(self, "__proxyOnObj", [obj])


def proxying(cls):
    if hasattr(cls, "__getattr__"):
        orig_getattr = cls.__getattr__

        def _getattr(self, k):
            try:
                return orig_getattr(self, k)
            except AttributeError:
                for i in self.__proxyOnObj:
                    if hasattr(i, k):
                        return getattr(i, k)
            raise AttributeError(k)

    else:

        def _getattr(self, k):
            for i in self.__proxyOnObj:
                if hasattr(i, k):
                    return getattr(i, k)
            raise AttributeError(k)

    if hasattr(cls, "__setattr__"):
        orig_setattr = cls.__setattr__

        def _setattr(self, k, v):
            try:
                return orig_setattr(self, k, v)
            except AttributeError:
                for i in self.__proxyOnObj:
                    if hasattr(i, k):
                        setattr(i, k, v)
            raise AttributeError(k)

    else:

        def _setattr(self, k, v):
            for i in self.__proxyOnObj:
                if hasattr(i, k):
                    setattr(i, k, v)
            setattr(self, k, v)

    setattr(cls, "__getattr__", _getattr)
    setattr(cls, "__setattr__", _setattr)
    setattr(cls, "__proxying", True)
    return cls


def clearDictNone(d):
    """in-place"""
    for k, v in list(d.items()):
        if not v:
            del d[k]
    return d


class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)
