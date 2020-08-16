def flatten(x):
   a = []
   for i in x:
      if isinstance(i, list):
         a.extend(flatten(i))
      else:
         a.append(i)
   return a

def take(n, it):
   i = 0
   for k in it:
      if i >= n:
         return
      yield k
      i += 1
   return
