from itertools import zip_longest
from sublist import sublist
from symbol import s, isSymbol, symbolName
import sys
sys.setrecursionlimit(50)

# makePattern :: Class -> Patternable Class
# Patternable Class :
#    __getitem__ :: tuple -> Matchable Class
# Matchable Class :
#    match :: value -> Dict | False


class _Matchable():

   def __init__(self, name, base_type, params):
      self.params = params
      self.name = name
      self.base_type = base_type

   def __str__(self):
      if self.params is None:
         return f"({self.name})"
      else:
         sParams = " ".join(str(i) for i in self.params)
         return f"({self.name} {sParams})"


class _Patternable():

   def __init__(self, name, matchable):
      self.name = name
      self.matchable = matchable

   def __getitem__(self, params):
      if not isinstance(params, tuple):
         params = (params,)
      return self.matchable(params)

   def __str__(self):
      return f"Patternable<{self.name}>"


def _updateResult(result, k, v):
   if k == s._:
      return
   if k in result:
      raise TypeError("Repeated Symbol")
   result[k] = v


def matchList(self: _Matchable, value):
   if not isinstance(value, list):
      return False

   if len(self.params) == 0 and len(value) != 0:
      return False

   head = sublist(self.params, 0, len(self.params) - 1)
   tail = sublist(self.params, len(self.params) - 1, len(self.params))[0]

   result = {}

   for p, v in zip(head, value):
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
   _updateResult(result, tail, list(sublist(value, len(head))))
   return result


def matchTuple(self: _Matchable, value):
   if not isinstance(value, tuple):
      return False
   if len(self.params) != len(value):
      return False
   result = {}
   for p, v in zip(self.params, value):
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
   if type(value) in _Mapping:
      params = tuple(toMatchable(i) for i in value)
      return _Mapping[type(value)].__getitem__(params)
   else:
      return value


# :: *args -> (match :: value -> Dict | False)
def defaultMatch(*args):

   def match(self: _Matchable, value):
      # args = ("x", "y", "z")
      # params = Class[s.x, s.y, s.z]
      # Class[s.x s.y s.z] -> Tuple[s.x s.y s.z]
      # Tuple[s.x s.y s.z] `match` tuple(x, y, z)
      # value :: object
      if not isinstance(value, self.__class__):
         return False
      return Tuple.__getitem__(self.params).match(tuple(getattr(value, name) for name in args))

   return match


def makePattern(name, cls, match):
   __init__ = lambda self, params: super(self.__class__, self).__init__(name, cls, params)
   _match = type(f"__Match{name}", (_Matchable,), {
       "__init__": __init__,
       "match": defaultMatch(match) if isinstance(match, tuple) else match
   })

   def __getitem__(self, params):
      if not isinstance(params, tuple):
         params = (params,)
      return _match(params)

   return _Patternable(name, _match)


List = makePattern("List", list, matchList)
Tuple = makePattern("Tuple", tuple, matchTuple)
_Mapping = {list: List, tuple: Tuple}

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

   # Empty List
   assert List[()].match([1, 2, 3]) == False
   assert List[()].match([1, 2, 3]) == False

   # Other
   assert List[(s.x, s.ys)].match([1, 2, 3]) == {s.x: 1, s.ys: [2, 3]}
   assert List[(s.x, s.y, s.z, s._)].match([1, 2, 3]) == {s.x: 1, s.y: 2, s.z: 3}
   assert List[(s.x, s.y, s.z, s.a)].match([1, 2, 3]) == {s.x: 1, s.y: 2, s.z: 3, s.a: []}
