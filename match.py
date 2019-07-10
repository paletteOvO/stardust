from itertools import zip_longest
from sublist import sublist
from symbol import s, isSymbol, symbolName, Symbol
import sys
sys.setrecursionlimit(50)

# makePattern :: Class -> Patternable Class
# Patternable Class :
#    __getitem__ :: tuple -> Matchable Class
# Matchable Class :
#    match :: value -> Dict | False


class _Matchable():

   def __init__(self, name, base_type, params):
      self.__params = params
      self.__name = name
      self.__type = base_type

   def __str__(self):
      if self.__params is None:
         return f"({self.__name})"
      else:
         s = self.__name + " " + " ".join(str(i) for i in self.__params)
         return f"({s})"


class _Patternable():

   def __init__(self, name, base_type, matchable):
      self.__name = name
      self.__matchable = matchable
      self.__type = base_type

   def __getitem__(self, params):
      # x[a, b, c] x[(a, b, c)] x[[]] x[[a, b, c]] x[()]
      if not isinstance(params, (tuple,)):
         params = (params,)
      return self.__matchable(self.__name, self.__type, params)


def _updateResult(result, k, v):
   if k == s._:
      return
   if k in result:
      raise TypeError("Repeated Symbol")
   result[k] = v


def matchList(self: _Matchable, value):

   if not isinstance(value, list):
      return False

   if len(self._Matchable__params) == 0:
      return {} if len(value) == 0 else False

   head = sublist(self._Matchable__params, 0, len(self._Matchable__params) - 1)
   tail = self._Matchable__params[-1]
   if not isinstance(tail, (list, Symbol)):
      raise SyntaxError("last element of pattern must be list or symbol")

   headValue = sublist(value, 0, len(head))
   tailValue = sublist(value, len(headValue))

   result = {}

   def loop(p, v):
      if isinstance(p, _Matchable):
         matched = p.match(v)
         # matched :: False | Dict
         if matched != False:
            for k, v in matched:
               _updateResult(result, k, v)
         else:
            return False
      elif isSymbol(p):
         _updateResult(result, p, v)
      else:
         if p != v:
            return False

   # match head
   for p, v in zip_longest(head, headValue):
      if loop(p, v) == False:
         return False
   # match tail
   if isSymbol(tail):
      _updateResult(result, tail, tailValue)
   else:
      for p, v in zip_longest(tail, tailValue):
         if loop(p, v) == False:
            return False

   return result


def matchTuple(self: _Matchable, value):
   if not isinstance(value, tuple):
      return False
   if len(self._Matchable__params) != len(value):
      return False
   result = {}
   for p, v in zip(self._Matchable__params, value):
      if isinstance(p, _Matchable):
         matched = p.match(v)
         # matched :: False | Dict
         if matched != False:
            for k, v in matched:
               _updateResult(result, k, v)
         else:
            return False
      elif isSymbol(p):
         _updateResult(result, p, v)
      else:
         if v != p:
            return False
   return result


def toMatchable(value):
   _Mapping = {list: List, tuple: Tuple}
   if type(value) in _Mapping:
      params = tuple(toMatchable(i) for i in value)
      return _Mapping[type(value)].__getitem__(params)
   else:
      return value


# :: *args -> (match :: value -> Dict | False)
def defaultMatch(args):

   def match(self: _Matchable, value):
      # args = ("x", "y", "z")
      # params = Class[s.x, s.y, s.z]
      # Class[s.x s.y s.z] -> Tuple[s.x s.y s.z]
      # Tuple[s.x s.y s.z] `match` tuple(x, y, z)
      # value :: object
      if not isinstance(value, self._Matchable__type):
         return False
      return Tuple.__getitem__(self._Matchable__params).match(
          tuple(getattr(value, name) for name in args))

   return match


def implMatchable(cls, match):
   setattr(cls, "match", defaultMatch(match) if isinstance(match, tuple) else match)
   return cls


def makePattern(name, cls, match):
   __init__ = lambda self, name, base_type, params: super(self.__class__, self).__init__(
       name, cls, params)
   matchCls = type(f"__Match_{name}", (_Matchable,), {"__init__": __init__})
   implMatchable(matchCls, match)
   return _Patternable(name, cls, matchCls)


List = makePattern("List", list, matchList)
Tuple = makePattern("Tuple", tuple, matchTuple)


def dataclass(name, *data):

   def __init__(self, *args, **kwargs):
      if len(args) != len(data):
         raise TypeError()
      for k, v in zip(data, args):
         setattr(self, k, v)

   target = type(
       name, (), {
           "__init__":
           __init__,
           "instanceof":
           lambda self, value: isinstance(self, value._Patternable__type) if isinstance(
               value, _Patternable) else isinstance(self, value)
       })

   def __call__(self, *args, **kwargs):
      return target(*args, **kwargs)

   x: _Patternable = type(name, (_Patternable,), {"__call__": __call__})

   matchCls = type(f"__Match_{name}", (_Matchable,), {})
   implMatchable(matchCls, tuple(data))
   ret = x(name, target, matchCls)
   return ret


Just = dataclass("Just", "a")
# Just("") -> object
# Just[s.x] -> matchable

if __name__ == "__main__":
   from symbol import s

   # Empty Tuple
   assert Tuple[()].match(tuple()) == {}
   assert Tuple[()].match((1,)) == False

   # 1-Tuple
   assert Tuple[s._].match(tuple()) == False

   assert Tuple[s._].match((1,)) == {}
   assert Tuple[s.x].match((1,)) == {s.x: 1}

   assert Tuple[s.x].match((1, 2)) == False

   # 2-Tuple
   assert Tuple[s._, s._].match((1, 2)) == {}
   assert Tuple[s.x, s._].match((1, 2)) == {s.x: 1}
   assert Tuple[s._, s.x].match((1, 2)) == {s.x: 2}
   assert Tuple[s.x, s.y].match((1, 2)) == {s.x: 1, s.y: 2}

   assert Tuple[s.x, s.y].match(tuple()) == False
   assert Tuple[s.x, s.y].match((1,)) == False
   assert Tuple[s.x, s.y].match((1, 2, 3)) == False

   # List[[1, 2, 3]] == List[1, 2, 3, []]
   assert List[[1, 2, 3]].match([1, 2, 3]) == {}
   assert List[1, 2, 3, []].match([1, 2, 3]) == {}

   # It should raise syntax error i guess...
   # assert List[1, 2, 3].match([1, 2, 3]) == False

   # Empty List
   assert List[[],].match([]) == {}
   assert List[1, []].match([]) == False
   assert List[[]].match([1, 2, 3]) == False

   # It doesn't make sense actually
   assert List[()].match([1, 2, 3]) == False

   # value match
   assert List[[1]].match([1]) == {}
   assert List[1, 2, 3, []].match([1, 2, 3]) == {}

   # Other
   assert List[s.x, s.ys].match([1, 2, 3]) == {s.x: 1, s.ys: [2, 3]}
   assert List[(s.x, s.y, s.z, s._)].match([1, 2, 3]) == {s.x: 1, s.y: 2, s.z: 3}
   assert List[(s.x, s.y, s.z, s.a)].match([1, 2, 3]) == {s.x: 1, s.y: 2, s.z: 3, s.a: []}

   # not match
   assert List[[s.x, s.y, s.z, 1]].match([1, 2, 3]) == False

   # I think they are basically the same thing
   print(Just[s._].match(Just(1)) is not False)
   print(Just(1).instanceof(Just))
