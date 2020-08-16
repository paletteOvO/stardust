import inspect
from functools import wraps, partial
from .pipe_fn import e
from .symbol import s

_t = lambda *args, **kwargs: True
_n = lambda *args, **kwargs: None

class Cond():
   def __init__(self, func, *, filter=_t, argsCheck=_t, resultCheck=_t):
      self.func = func
      self._filter = [filter]
      self._argsCheck = [argsCheck]
      self._resultCheck = [resultCheck]

   def addFilter(self, filter):
      self._filter.insert(0, filter)

   def addArgsCheck(self, argsCheck):
      self._argsCheck.insert(0, argsCheck)

   def addResultCheck(self, resultCheck):
      self._resultCheck.insert(0, resultCheck)

   def filter(self, args, kwargs):
      return all(f(args, kwargs) for f in self._filter)

   def argsCheck(self, args, kwargs):
      return all(f(args, kwargs) for f in self._argsCheck)

   def resultCheck(self, result):
      return all(f(result) for f in self._resultCheck)

def getWrapped(func, getter):
   if hasattr(func, '__wrapped__'):
      return getWrapped(func.__wrapped__, getter)
   return getter(func)

def getFuncName(func):
   return getWrapped(func, lambda f: f.__name__)

def getFuncAnno(func):
   return getWrapped(func, lambda f: f.__annotations__)

def getFuncArgs(func):
   return getWrapped(func, lambda f: f.__code__.co_varnames)

def getFuncTable(func):
   # module.functable : Dict[FuncName -> a]; a = Dict[FuncId -> Cond]
   import sys
   module = sys.modules[getWrapped(func, lambda f: f.__module__)]

   if "__stardust__functable" not in module.__dict__:
      module.__stardust__functable = dict()

   if getFuncName(func) not in module.__stardust__functable:
      module.__stardust__functable[getFuncName(func)] = dict()

   return module.__stardust__functable[getFuncName(func)]

def getFuncId(func):
   return getWrapped(func, id)

def getFuncCond(func):
   func_table = getFuncTable(func) # : Dict[FuncId -> [Cond]]
   if getFuncId(func) not in func_table:
      func_table[getFuncId(func)] = Cond(func)
   return func_table[getFuncId(func)]

def mergeArgs(var_lst, args, kwargs):
   copied_args = list(args)
   merged_args = dict(kwargs)
   for i in var_lst:
      if i not in kwargs:
        merged_args[i] = copied_args.pop(0)
   return merged_args

def genTypeTable(kwargs):
   type_table = {}
   for k, v in kwargs.items():
      type_table[k] = type(v)
   return type_table

def callWrapper(func):
   func_table = getFuncTable(func) # : Dict[FuncId -> Cond]
   def call(*args, **kwargs):
      for cond in func_table.values():
         if cond.filter(args, kwargs): # for dispatch, predicate
            cond.argsCheck(args, kwargs) # for refine, it should throw exception or do nothing
            res = cond.func(*args, **kwargs)
            cond.resultCheck(res) # for refine, it should throw exception or do nothing
            return res
      raise Exception(f"No suitable func for {getFuncName(func)}")
   return wraps(func)(call)


# type check, multi dispatch
def dispatch(func):
   expected_type = getFuncAnno(func)
   var_lst = getFuncArgs(func)

   def _dispatchFilter(args, kwargs):
      if not is_suitable(func, args, kwargs):
         return False

      type_table = genTypeTable(mergeArgs(var_lst, args, kwargs))

      match = True
      for args_name, args_type in expected_type.items():
         if not issubclass(type_table[args_name], args_type):
            match = False
            break

      return match

   getFuncCond(func).addFilter(_dispatchFilter)

   return callWrapper(func)

def predicate(check_func):
   return partial(_predicate0, check_func)

def match(*args, **kwargs):
   return partial(_match0, args, kwargs)

def _match0(expected_args, expected_kwargs, func):
   var_lst = getFuncArgs(func)

   def _matchFilter(args, kwargs):
      if not is_suitable(func, args, kwargs):
         return False

      return testMatch(expected_args, args) and testMatch(expected_kwargs, kwargs)

   getFuncCond(func).addFilter(_matchFilter)

   return callWrapper(func)

def _predicate0(check_func, func):
   var_lst = getFuncArgs(func)
   cc_var_lst = getFuncArgs(check_func)

   def _predicateFilter(args, kwargs):
      if not is_suitable(func, args, kwargs):
         return False

      merged_args = mergeArgs(var_lst, args, kwargs)

      match = True
      if not check_func(**{k: merged_args[k] for k in cc_var_lst}):
         match = False

      return match

   getFuncCond(func).addFilter(_predicateFilter)

   return callWrapper(func)

def refine(*, In=None, Out=None):
   return partial(_refine0, In, Out)

def _refine0(In, Out, func):
   cond = getFuncCond(func)

   if In:
      cc = In
      cc_var_lst = getFuncArgs(cc)
      def _refineInCheck(*args, **kwargs):
         a = mergeArgs(cc_var_lst, args, kwargs)
         if not cc(**a):
            raise TypeError(f"In check failed at {cc}")
         return True

      cond.addArgsCheck(_refineInCheck)

   if Out:
      cc = Out
      cc_var_lst = getFuncArgs(cc)
      def _refineOutCheck(*args, **kwargs):
         a = mergeArgs(cc_var_lst, args, kwargs)
         if not cc(**a):
            raise TypeError(f"Out check failed at {cc}")
         return True

      cond.addResultCheck(_refineOutCheck)

   return callWrapper(func)

def is_suitable(func, args, kwargs):
   func_argspec = inspect.getfullargspec(func)

   if not (len(args) == len(func_argspec.args) or \
            (len(args) > len(func_argspec.args) and func_argspec.varargs is not None)):
      return False

   if [i for i in kwargs.keys() if i not in func_argspec.args] and \
         func_argspec.varkw is None:
      return False

   return True

def testMatch(patt, obj):
   if patt == s._ or patt == obj:
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
