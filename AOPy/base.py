import sys
from .weaver import install, uninstall

class AspectBase(object):
   '''
   Base class for all aspects.
   '''
   targets = []

   def __init__(self, next_callable, core_callable):
      self.next_callable = next_callable
      self.core_callable = core_callable
   
   @classmethod
   def enable(cls):
      for target in cls.targets:
         install(cls, target)

   @classmethod
   def disable(cls):
      for target in cls.targets:
         uninstall(cls, target)

   def before_advice(self, *args, **kwargs):
      pass

   def after_advice(self, retval, *args, **kwargs):
      pass

   def after_exception_advice(self, exception, *args, **kwargs):
      pass

class ExecutionBase(AspectBase):
   '''
   Base class for wrapping advice around each individual call.
   '''
   def __call__(self, *args, **kwargs):
      self.before_advice(*args, **kwargs)
      try:
         result = self.next_callable(*args, **kwargs)
      except Exception as e:
         self.after_exception_advice(e, *args, **kwargs)
         raise
      else:
         self.after_advice(result, *args, **kwargs)
      return result

class CallBase(AspectBase):
   # This may be unnecessary as a base class. The advice methods in an
   # ExecutionBase can simply call sys._getframe(2) on their own. I just haven't
   # found a simple, readable, and efficient way to produce this behavior by
   # simply parameterizing ExecutionBase, so it's a matter of taste. This aspect
   # really should also maintain a mapping from the original code object to the
   # original method object to make more debugging information available.
   def __call__(self, *args, **kwargs):
      self.caller = sys._getframe(1).f_code
      self.before_advice(*args, **kwargs)
      try:
         result = self.next_callable(*args, **kwargs)
      except Exception as e:
         self.after_exception_advice(e, *args, **kwargs)
         raise
      else:
         self.after_advice(result, *args, **kwargs)
      return result

class DepthBase(AspectBase):
   '''
   Base class for aspects that track the depth of the call stack.
   '''
   # We use this trick to avoid using metaclasses or requiring the user to
   # remember to call the super's __init__ method when subclassing:
   # http://docs.python.org/2/reference/simple_stmts.html#attr-target-note
   #
   # The right way to do this is with metaclasses, but Tim Peters has scared
   # enough people away from them that I thought it better to use this horrible
   # hack instead. It's rather unpythonic, but then so is Python in this case.
   depth = 0

   def __call__(self, *args, **kwargs):
      self.before_advice(*args, **kwargs)
      self.__class__.depth += 1
      try:
         result = self.next_callable(*args, **kwargs)
      except Exception as e:
         self.__class__.depth -= 1
         self.after_exception_advice(e, *args, **kwargs)
         raise
      else:
         self.__class__.depth -= 1
         self.after_advice(result, *args, **kwargs)
      return result

   def active(self):
      return self.__class__.depth > 0

class CFlowMeta(type):
   def __new__(meta, classname, supers, classdict):
      classdict["within_cflow"] = False
      return type.__new__(meta, classname, supers, classdict)
      
class CFlowBase(AspectBase):
   '''
   Base class for cflow-style aspects.
   This may be something of a misnomer. More specifically, it behaves like
   execution(pointcut) && !cflowbelow(execution(pointcut)) in AspectJ terms. The
   before and after advice runs only around targets that are not called as a
   consequence of any other target. This behavior could be implemented on an
   ExecutionBase-derived class by checking the boolean flag from within the
   advice methods, but this way we save a bunch of do-nothing function calls. I
   haven't yet checked whether this has a significant impact on performance in
   deep call stacks.
   '''
   # Same trick as in DepthBase.
   within_cflow = False

   def __call__(self, *args, **kwargs):
      if self.__class__.within_cflow:
         return self.next_callable(*args, **kwargs)
      else:
         self.before_advice(*args, **kwargs)
         self.__class__.within_cflow = True
         try:
            result = self.next_callable(*args, **kwargs)
         except Exception as e:
            self.__class__.within_cflow = False
            self.after_exception_advice(e, *args, **kwargs)
            raise
         else:
            self.__class__.within_cflow = False
            self.after_advice(result, *args, **kwargs)
         return result

   def active(self):
      return self.__class__.within_cflow

# For the next aspect, the scoping trick from DepthBase won't work, so we have
# to use a metaclass.
class CoverageMeta(type):
   def __new__(meta, classname, supers, classdict):
      classdict["instances"] = set()
      return type.__new__(meta, classname, supers, classdict)
      
class CoverageBase(ExecutionBase):
   '''
   Base class for identifying functions and methods that have not been used.
   A quick and dirty way to focus the programmer's attention on potentially
   orphaned code. This is best used in a REPL-like environment so you can query
   the `instances` class variable.
   '''
   __metaclass__ = CoverageMeta
   
   def __init__(self, next_callable, core_callable):
      super(CoverageBase, self).__init__(next_callable, core_callable)
      self.__class__.instances.add(self.core_callable)
   def before_advice(self, *args, **kwargs):
      if self.core_callable in self.__class__.instances:
         self.__class__.instances.remove(self.core_callable)
