from functools import reduce, update_wrapper


def pipe_call(a, b):
   return b(a)


def and_then(*f):

   def and_then_call(x):
      return reduce(pipe_call, f, x)

   return and_then_call


class Pipe:

   def __init__(self, f, l_args, r_args, kwargs, f_continue: tuple = None):
      if isinstance(f, str):
         self.as_instance = True
      else:
         update_wrapper(self, f)
         self.as_instance = False

      self.f = f
      self.f_continue = f_continue
      self.l_args = l_args
      self.r_args = r_args
      self.kwargs = kwargs

   def __truediv__(self, other):
      return Pipe(other, self.l_args, self.r_args, self.kwargs)

   def __getattr__(self, name):
      return Pipe(name, self.l_args, self.r_args, self.kwargs)

   def __pow__(self, kwargs):
      kwargs.update(self.kwargs)
      return Pipe(self.f, self.l_args, self.r_args, self.kwargs)

   def __mul__(self, args):
      if not isinstance(args, tuple):
         args = (args,)
      return Pipe(self.f, self.l_args, self.r_args + args, self.kwargs)

   def __matmul__(self, args):
      if not isinstance(args, tuple):
         args = (args,)
      return Pipe(self.f, self.l_args + args, self.r_args, self.kwargs)

   def __call__(self, left):
      if isinstance(self.f, str):
         v = getattr(left, self.f)(*self.l_args, *self.r_args, **self.kwargs)
      else:
         v = self.f(*self.l_args, left, *self.r_args, **self.kwargs)
      if not self.f_continue:
         return v
      else:
         return reduce(pipe_call, self.f_continue, v)

   def __ror__(self, left):
      return self(left)


e = Pipe(lambda x: x, (), (), dict())
