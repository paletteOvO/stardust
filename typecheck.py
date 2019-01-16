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


