from typing import List, Dict, Tuple, Any

class Symbol():
   def __init__(self, name):
      self.name = name
   def __eq__(self, other):
      return other is not None and isinstance(other, self.__class__) and other.name == self.name
   def __repr__(self):
      return f"Symbol<{self.name}>"
   def __getattr__(self, name):
      return self.__class__(self.name + "." + name)

class s():
   def __init__(self, symCls):
      self.symCls = symCls
   def __getattr__(self, name):
      return self.symCls(name)

s = s(Symbol)
del Symbol

typeMap = [
   (List, list),
   (Dict, dict),
   (Tuple, tuple),
   (int, int),
   (float, float),
]

collectionType = [
   List, Dict, Tuple
]

def toBaseType(typingType):
   for i in typeMap:
      if typingType == i[0]:
         return (i[1], s.ok)
   raise ("type is not in typeMap", s.err)

def checktype(value, typingType):
   t, err = toBaseType(type(value))


   pass
