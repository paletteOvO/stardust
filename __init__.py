from types import FunctionType
import inspect
from functools import wraps


"""make life easier"""

from .pipe_fn import e
from .symbol import s
from .netutil import *
from .funcional import flatten
from .hash import djb2, fnv32a
from .deco import dispatch, predicate, refine

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


# ==


def clearDictNone(d):
    """in-place"""
    for k, v in list(d.items()):
        if not v:
            del d[k]
    return d


class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)


class _CaseMatching:
    def __init__(self, obj):
        self.pt = []
        self.obj = obj
        pass

    def __or__(self, case):
        self.pt.append(case)
        return self

    def end(self):
        for case in self.pt:
            if isinstance(case.check, FunctionType) and case.check():
                return case.result()
            if (
                self.obj is not None
                and inspect.isclass(case.check)
                and isinstance(self.obj, case.check)
            ):
                var_lst = case.result.__code__.co_varnames
                return case.result(**{k: getattr(self.obj, k) for k in var_lst})
            if self.obj is not None and self.obj == case.check:
                return case.result()
        raise Exception()


class case:
    def __init__(self, check):
        self.check = check

    def __rshift__(self, result):
        self.result = result
        return self


def when(objOrf, f=None):
    if f is not None:
        a = _CaseMatching(objOrf)
    else:
        a = _CaseMatching(None)
        f = objOrf
    f(a)
    return a.end()


def value(v):
    return lambda: v


otherwise = case(lambda: True)
