from types import FunctionType
import inspect


class _CaseMatching:

   def __init__(self, obj):
      self.otherwise = value(True)
      self.pt = []
      self.obj = obj

   def __or__(self, case):
      self.pt.append(case)
      return self

   def end(self):
      for eachcase in self.pt:
         if eachcase.check(self.obj):
            return eachcase.result()
      raise Exception()


class _BaseCase():

   def check(self, obj):
      raise NotImplementedError()

   def __init__(self, v):
      self.v = v

   def __rshift__(self, result):
      self.r = result
      return self

   def result(self):
      return self.r()


class case(_BaseCase):

   def check(self, obj):
      return self.v()


class value(_BaseCase):

   def check(self, obj):
      return self.v == obj

   def __call__(self):
      return self.v


class pattern(_BaseCase):

   def check(self, obj):
      # if inspect.isclass(case.check) and isinstance(self.obj, case.check):
      # var_lst = case.result.__code__.co_varnames
      # return case.result(**{k: getattr(self.obj, k) for k in var_lst})
      # TODO
      return False


otherwise = case(lambda: True)


def when(objOrf, f=None):
   if f is not None:
      a = _CaseMatching(objOrf)
   else:
      a = _CaseMatching(None)
      f = objOrf
   if f.__code__.co_argcount == 2:
      f(a, objOrf)
   else:
      f(a)
   return a.end()
