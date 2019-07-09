from itertools import zip_longest
from sublist import sublist
from symbol import s, isSymbol, symbolName
import sys
sys.setrecursionlimit(50)


class _Container():

   def __init__(self, name, base_type):
      self.name = name
      self.base_type = base_type

   def isInstance(self, value):
      return isinstance(value, self.base_type) and self.__checkContainer(value)

   def __str__(self):
      if self.params is None:
         return f"({self.name})"
      else:
         sParams = " ".join(str(i) for i in self.params)
         return f"({self.name} {sParams})"


class _List(_Container):

   def __init__(self, params):
      self.name = "List"
      self.params = [toContainer(i) for i in params]

   def match(self, value):
      if not isinstance(value, list):
         return False

      if len(self.params) == 0 and len(value) != 0:
         return False

      head = sublist(self.params, 0, len(self.params) - 1)
      tail = sublist(self.params, len(self.params) - 1, len(self.params))[0]

      result = {}

      for p, v in zip(head, value):
         if isinstance(p, _Container):
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


class _Tuple(_Container):

   def __init__(self, params):
      self.name = "Tuple"
      self.params = [toContainer(i) for i in params]

   def match(self, value):
      if not isinstance(value, tuple):
         return False
      if len(self.params) != len(value):
         return False
      result = {}
      for p, v in zip(self.params, value):
         if isinstance(p, _Container):
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


def toContainer(value):
   if isinstance(value, list):
      # [1, 2, 3, s.x, []]
      listParams = tuple(toContainer(i) for i in value)
      return List.__getitem__(listParams)
   elif isinstance(value, tuple):
      tupleParams = tuple(toContainer(i) for i in value)
      return Tuple.__getitem__(tupleParams)
   else:
      return value


def _updateResult(result, k, v):
   if k == s._:
      return
   if k in result:
      raise TypeError("Repeated Symbol")
   result[k] = v


class _Maker():

   def __init__(self, target):
      self.target = target

   def __getitem__(self, params):
      if not isinstance(params, tuple):
         params = (params,)
      x = self.target(params)
      return x


List = _Maker(_List)
Tuple = _Maker(_Tuple)


# match(List[s.x, s.y, s._], [1, 2])(Out=lambda x, y: x + y)
def match(pattern, value):
   return lambda Out: _match(pattern, value, Out)


def _match(pattern, value, Out):
   if isinstance(value, list):
      if not isinstance(pattern, List):
         return False


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
