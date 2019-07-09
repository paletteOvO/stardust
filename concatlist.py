class concatlist():

   def __init__(self, *lists):
      """
      Concat list
      """
      self.lists = lists
      self.length = sum(len(i) for i in lists)

   def __len__(self):
      return self.length

   def __getitem__(self, index):
      if index > self.length or index < 0:
         raise IndexError(index)

      offset = 0
      for l in self.lists:
         if index >= offset + len(l):
            offset += len(l)
         else:
            return l[index - offset]

   def __repr__(self):
      return "[" + "|".join(repr(i) for i in self.lists) + "]"

   def __str__(self):
      return repr(self)

   def __eq__(self, value):
      if not isinstance(value, list) and not isinstance(value, concatlist):
         return False
      if len(value) != len(self):
         return False
      for a, b in zip(self, value):
         if a != b:
            return False
      return True

   def __iter__(self):
      return ConcatListIter(self)


class ConcatListIter():

   def __init__(self, concatlist):
      self.concatlist = concatlist
      self.index = 0
      self.end = len(concatlist)

   def __next__(self):
      if self.index < self.end:
         self.index += 1
         return self.concatlist[self.index - 1]
      else:
         raise StopIteration()


if __name__ == "__main__":
   assert concatlist([]) == []
   assert concatlist([1, 2, 3]) == [1, 2, 3]
   assert concatlist([1, 2], [0], [2]) == [1, 2, 0, 2]
