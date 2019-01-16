from .pipe_fn import e
from .symbol import s
from .netutil import POST, GET, POST_json, GET_json, POST_data
from .funcional import flatten
from .hash import djb2, fnv32a
from .dispatch import dispatch, predicate, refine, match
from .case import when, case, otherwise, value

def main():
   @dispatch
   @predicate(lambda x: x >= 0)
   @refine(Out=lambda res: res >= 0)
   def abs(x: int):
      return x

   @dispatch
   @predicate(lambda x: x < 0)
   @refine(Out=lambda res: res >= 0)
   def abs(x: int):
      return -x

   assert abs(10) == 10
   assert abs(-10) == 10

   assert (-10 | e/abs) == 10
   assert when(lambda s: s
      | case(lambda: False) >> value(1)
      | case(lambda: False) >> value(2)
      | otherwise >> value(3)
      ) == 3
