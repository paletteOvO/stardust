from .symbol import Nothing

class Seq():
   def __init__(self, iterable):
      self._i = iterable

   def __next__(self):
      return self._i.__next__()

   def __iter__(self):
      return self

   def map(self, f):
      return Seq(f(i) for i in self._i)

   def sum(self):
      return

   def tolist(self):
      return list(self._i)

   def filter(self, f):
      return Seq(i for i in self._i if f(i))

   def foldl(self, f, default):
      left = default

      while True:
         try:
            left = f(left, self._i.__next__())
         except StopIteration:
            return left

      return

   def foldl1(self, f):
      return self.foldl(f, self._i.__next__())

   def foldr(self, f, default=Nothing):
      if default == Nothing:
         [1, 2]
         f(1, 2)

         [1, 2, 3]
         f(1, f(2, 3))

         [1, 2, 3]
         f(f(1, 2), 3)

         # foldl' f [] init = init
         # foldl' f [x:xs] init = foldl' f xs (f init x)

         # foldl f [x:y:[]] = f x y
         # foldl f [x:y:xs] = foldl f (f x y) : xs

      else:
         right = default

seq = Seq
