import inspect
from operator import add

def all_classes(*modules):
   return reduce(add,
                 [[pair[1] for pair in
                   inspect.getmembers(mod, predicate=inspect.isclass)]
                  for mod in modules])

def all_methods(*classes):
   return reduce(add,
                 [[pair[1] for pair in
                   inspect.getmembers(class_, predicate=inspect.ismethod)]
                  for class_ in classes])

def direct_methods(*classes):
   '''
   Get the methods defined on given classes but not inherited from superclasses.
   I'm not sure if this is strictly correct. Using the __new__/__init__ methods
   on metaclasses would help us unambiguously determine which methods are
   directly defined on a class, but forcing the use of metaclasses would
   undermine the goal of obliviousness.
   '''
   return reduce(add,
                 [[pair[1] for pair in
                   inspect.getmembers(class_, predicate=inspect.ismethod)
                   if pair[0] in vars(class_)] for class_ in classes])
