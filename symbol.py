class Symbol():
   def __init__(self, name):
      self.name = name
   def __eq__(self, other):
      return other is not None and isinstance(other, self.__class__) and other.name == self.name
   def __repr__(self):
      return f"Symbol<{self.name}>"
   def __getattr__(self, name):
      return self.__class__(self.name + "." + name)
   def __hash__(self):
      return hash(repr(self))

class s():
   def __init__(self, symCls):
      self.symCls = symCls
   def __getattr__(self, name):
      return self.symCls(name)

s = s(Symbol)
del Symbol

Nothing = s.Nothing
