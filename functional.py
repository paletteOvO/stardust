def flatten(x):
   a = []
   for i in x:
      if isinstance(i, list):
         a.extend(flatten(i))
      else:
         a.append(i)
   return a
