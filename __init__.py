from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
from types import FunctionType
import inspect
from functools import wraps
from pipe_fn import e

"""make life easier"""

class _Nothing():
   pass

Nothing = _Nothing()

def asProperty(obj, name, getter=Nothing, setter=Nothing, default=Nothing):
   cls = obj.__class__
   propName = f"_{name}"
   if default != Nothing:
      setattr(obj, propName, default)
   if getter == Nothing:

      def _getter(self):
         return getattr(self, propName)

      getter = _getter
   if setter == Nothing:
      setattr(cls, name, property(getter))
   else:

      def _setter(self, v):
         setattr(self, propName, v)

      setattr(cls, name, property(getter, setter or _setter))


def proxyOn(self, obj):
   if '__proxyOnObj' in dir(self):
      self.__proxyOnObj.append(obj)
   else:
      if 'proxying' not in dir(self.__class__):
         proxying(self.__class__)
      setattr(self, "__proxyOnObj", [obj])


def proxying(cls):
   if hasattr(cls, "__getattr__"):
      orig_getattr = cls.__getattr__

      def _getattr(self, k):
         try:
            return orig_getattr(self, k)
         except AttributeError:
            for i in self.__proxyOnObj:
               if hasattr(i, k):
                  return getattr(i, k)
         raise AttributeError(k)
   else:
      def _getattr(self, k):
         for i in self.__proxyOnObj:
            if hasattr(i, k):
               return getattr(i, k)
         raise AttributeError(k)

   if hasattr(cls, "__setattr__"):
      orig_setattr = cls.__setattr__

      def _setattr(self, k, v):
         try:
            return orig_setattr(self, k, v)
         except AttributeError:
            for i in self.__proxyOnObj:
               if hasattr(i, k):
                  setattr(i, k, v)
         raise AttributeError(k)
   else:

      def _setattr(self, k, v):
         for i in self.__proxyOnObj:
            if hasattr(i, k):
               setattr(i, k, v)
         setattr(self, k, v)

   setattr(cls, "__getattr__", _getattr)
   setattr(cls, "__setattr__", _setattr)
   setattr(cls, "__proxying", True)
   return cls


def POST(url, headers=dict(), data=dict()):
   request = Request(url, urlencode(data).encode())
   for k in headers:
      request.add_header(k, headers[k])
   return urlopen(request)


def GET(url, headers=dict()):
   request = Request(url)
   for k in headers:
      request.add_header(k, headers[k])
   return urlopen(request)


def GET_json(url, headers=dict()):
   return json.loads(
       GET(url, headers).read().decode("unicode-escape").replace('\r\n', ''), strict=False)


def POST_json(url, headers=dict(), data=dict()):
   return json.loads(
       POST(url, headers, data).read().decode("unicode-escape").replace('\r\n', ''), strict=False)


def POST_data(url, data, headers=dict()):
   request = Request(url)
   for k in headers:
      request.add_header(k, headers[k])
   return urlopen(request, data)


# ==
def djb2(string):
   hashCode = 5381
   for i in string:
      hashCode = ((hashCode << 5) + hashCode) + ord(i)
   return hashCode


def fnv32a(str):
   hashCode = 0x811c9dc5
   fnv_32_prime = 0x01000193
   uint32_max = 2**32
   for s in str:
      hashCode ^= ord(s)
      hashCode *= fnv_32_prime
   return hashCode & (uint32_max - 1)


def clearDictNone(d):
   """in-place"""
   for k, v in list(d.items()):
      if not v:
         del d[k]
   return d


class Bunch(object):

   def __init__(self, adict):
      self.__dict__.update(adict)


def dispatch(func):
   if not hasattr(dispatch, "func_table"):
      dispatch.func_table = {}

   n = func.__module__ + "." + func.__name__

   if n not in dispatch.func_table:
      dispatch.func_table[n] = []

   func_table = dispatch.func_table[n]

   type_table = func.__annotations__
   var_lst = func.__code__.co_varnames

   func_table.append((type_table, func))

   @wraps(func)
   def dispatch_wrapper(*args, **kwargs):
      target_func = _dispatch_get_func(n, args, kwargs)

      return target_func(*args, **kwargs)

   return dispatch_wrapper


def _merge_args(var_lst, args, kwargs):
   copied_args = list(args)
   merged_args = dict(kwargs)
   for i in var_lst:
      if i not in kwargs:
        merged_args[i] = copied_args.pop(0)
   return merged_args


def _gen_type_table(kwargs):
   type_table = {}
   for k, v in kwargs.items():
      type_table[k] = type(v)
   return type_table


def _dispatch_get_func(name, args, kwargs):

   func_list = dispatch.func_table[name]


   for expected_type, func in func_list:
      if not is_suitable(func, args, kwargs):
         continue

      var_lst = func.__code__.co_varnames
      type_table = _gen_type_table(_merge_args(var_lst, args, kwargs))

      match = True
      for args_name, args_type in expected_type.items():
         if not issubclass(type_table[args_name], args_type):
            match = False
            break

      if match:
         return func

   raise TypeError()


def predicate(*check_func):
   def predicate0(func):
      if not hasattr(predicate, "func_table"):
         predicate.func_table = {}

      n = func.__module__ + "." + func.__name__
      if n not in predicate.func_table:
         predicate.func_table[n] = []

      predicate.func_table[n].append((check_func, func))

      @wraps(func)
      def predicate_wrapper(*args, **kwargs):
         target_func = _predicate_get_func(n, args, kwargs)
         return target_func(*args, **kwargs)

      return predicate_wrapper
   return predicate0

def _predicate_get_func(name, args, kwargs):
   func_list = predicate.func_table[name]

   for check_func, func in func_list:

      if not is_suitable(func, args, kwargs):
         continue

      var_lst = func.__code__.co_varnames
      merged_args = _merge_args(var_lst, args, kwargs)

      match = True
      for cc in check_func:
         cc_var_lst = cc.__code__.co_varnames
         if not cc(**dict((k, merged_args[k]) for k in cc_var_lst)):
            match = False
            break

      if match:
         return func

   raise TypeError()

def is_suitable(func, args, kwargs):
   func_argspec = inspect.getfullargspec(func)

   if not (len(args) == len(func_argspec.args) or \
            (len(args) > len(func_argspec.args) and func_argspec.varargs is not None)):
      return False

   if [i for i in kwargs.keys() if i not in func_argspec.args] and \
         func_argspec.varkw is None:
      return False

   return True

def curring(func):
   args = []
   @wraps(func)
   def curring0(x):
      args.append(x)
      if func.__code__.co_argcount == len(args):
         return func(*args)
      return curring0
   return curring0

def cached(func):
   if not hasattr(cached, "cache"):
      cached.cache = {}
   @wraps(func)
   def cached_wrapper(*args, **kwargs):
      if func.__name__ not in cached.cache:
         cached.cache[func.__name__] = {}
      if args not in cached.cache[func.__name__]:
         cached.cache[func.__name__][args] = func(*args)
      return cached.cache[func.__name__][args]
   return cached_wrapper

class _CaseMatching():
   def __init__(self, obj):
      self.pt = []
      self.obj = obj
      pass

   def __or__(self, case):
      self.pt.append(case)
      return self

   def end(self):
      for case in self.pt:
         if isinstance(case.check, FunctionType) and case.check():
            return case.result()
         if self.obj is not None and \
               inspect.isclass(case.check) and isinstance(self.obj, case.check):
            var_lst = case.result.__code__.co_varnames
            return case.result(**{k: getattr(self.obj, k) for k in var_lst})
         if self.obj is not None and self.obj == case.check:
            return case.result()
      raise Exception()


class case():
   def __init__(self, check):
      self.check = check
   def __rshift__(self, result):
      self.result = result
      return self

def when(objOrf, f=None):
   if f is not None:
      a = _CaseMatching(objOrf)
   else:
      a = _CaseMatching(None)
      f = objOrf
   f(a)
   return a.end()

def value(v):
   return lambda: v

otherwise = case(lambda: True)

def refine(*In, Out=None):
   def refine0(func):
      @wraps(func)
      def f(*args, **kwargs):
         a = _merge_args(func.__code__.co_varnames, args, kwargs)
         for i, cc in enumerate(In, 1):
            if not cc(**a):
               raise TypeError(f"Check fail at In[{i}]")
         result = func(**a)
         if Out:
            for i, cc in enumerate(Out, 1):
               if not cc(result):
                  raise TypeError(f"Check fail at Out[{i}]")
         return result
      return f
   return refine0

from functools import reduce
def flatten(x):
   a = []
   for i in x:
      if isinstance(i, list):
         a.extend(flatten(i))
      else:
         a.append(i)
   return a
