import functools
import types
import inspect
import collections

# Dictionary for retrieving the originally-created function/method object given
# its module, class (if applicable), and name
core_callables = {}

# Dictionary of lists of aspect instances wrapped on each core_callable
aspect_orderings = collections.defaultdict(list)

def get_key(obj):
   '''
   Generate a tuple to identify a location in the original program structure.
   '''
   return (inspect.getmodule(obj),
           obj.im_class if isinstance(obj, types.MethodType) else None,
           obj.__name__)

def install(Aspect, callable_):
   '''
   Wrap a new aspect as the outermost aspect atop callable_.
   '''
   key = get_key(callable_)
   if key not in core_callables:
      core_callables[key] = callable_
   core_callable = core_callables[key]
   for aspect_instance in aspect_orderings[core_callable]:
      if isinstance(aspect_instance, Aspect):
         # Don't allow multiple instances of an aspect on the same core_callable
         return
   aspect_orderings[core_callable].append(Aspect(None, core_callable))
   update_wrappings(core_callable)

def uninstall(Aspect, callable_):
   '''
   Remove aspect from whichever wrapping layer it appears in.
   '''
   key = get_key(callable_)
   if key in core_callables:
      core_callable = core_callables[key]

      # We don't currently allow more than one instance of the same aspect,
      # but this is here anyway
      to_remove = [aspect_instance
                   for aspect_instance in aspect_orderings[core_callable]
                   if isinstance(aspect_instance, Aspect)]
      if len(to_remove) == 0:
         return
      for aspect_instance in to_remove:
         aspect_orderings[core_callable].remove(aspect_instance)
      update_wrappings(core_callable)

def wrap_aspect(aspect_instance, next_callable):
   '''
   Modify existing aspect instance to wrap next_callable.
   '''
   aspect_instance.next_callable = next_callable
   @functools.wraps(next_callable)
   def wrapper(*args, **kwargs):
      return aspect_instance(*args, **kwargs)
   return wrapper

def update_wrappings(core_callable):
   '''
   Link all active aspects on core_callable with appropriate wrappings.
   '''
   aspect_ordering = aspect_orderings[core_callable]
   callable_ = core_callable
   for aspect_instance in aspect_ordering:
      callable_ = wrap_aspect(aspect_instance, callable_)
   if isinstance(core_callable, types.MethodType):
      setattr(core_callable.im_class, core_callable.__name__, callable_)
   else:
      setattr(inspect.getmodule(core_callable), core_callable.__name__, callable_)

def reset_all():
   '''
   Restore original callables and clear all bookkeeping data.
   '''
   aspect_orderings = collections.defaultdict(list)
   for core_callable_ in core_callables.itervalues():
      update_wrappings(core_callable)
   core_callables = {}
