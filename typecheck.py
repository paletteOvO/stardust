from typing import List, Dict, Tuple, Any
from .symbol import s

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

def testMatch(patt, obj):
   if patt == s._:
      return True
   if type(patt) != type(obj):
      return False
   if isinstance(obj, (set,)):
      if s._ in patt:
         return (patt - {s._}).issubset(obj)
      else:
         return testMatch(sorted(patt), sorted(obj))
   if isinstance(obj, (dict,)):
      if s._ in patt.keys():
         return testMatch(set(patt.values()), set(obj.values()))
      elif s._ in patt.values():
         return testMatch(set(patt.keys()), set(obj.keys()))
      else:
         return testMatch(sorted(patt.items()), sorted(obj.items()))
   if not isinstance(obj, (tuple, list)):
      return patt == obj
   if len(patt) != len(obj):
      return False
   for i, v in enumerate(obj):
      if patt[i] != s._ and not testMatch(patt[i], v):
         return False
   return True
