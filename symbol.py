class Symbol():

   def __init__(self, name):
      self.__data = {"name": name}

   def __eq__(self, other):
      return other is not None and \
               isinstance(other, self.__class__) and \
               other.__data["name"] == self.__data["name"]

   def __repr__(self):
      return f":{self.__data['name']}"

   def __getattr__(self, name, isData=False):
      if isData:
         return self.__data[name]
      else:
         return self.__class__(self.__data["name"] + "." + name)

   def __hash__(self):
      return hash(repr(self))

   def __str__(self):
      return repr(self)


class s():

   def __init__(self, symbolClass):
      self.symbolClass = symbolClass

   def __getattr__(self, name):
      return self.symbolClass(name)


_Symbol = Symbol
s = s(_Symbol)

Nothing = s.Nothing


def isSymbol(value):
   return isinstance(value, _Symbol)


def symbolName(symbol):
   return symbol.__getattr__("name", isData=True)


del Symbol
