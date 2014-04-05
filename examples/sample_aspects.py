from __future__ import print_function
import sample_classes
import collections
#import AOPy as aop
from AOPy import ExecutionBase, CFlowBase, DepthBase
from AOPy.utils import all_methods, all_classes



def redraw(trigger, obj):
   print(trigger, "on", obj, "made us redraw the screen")

class IncorrectObserverAspect(ExecutionBase):
   # Unlike in the typical Java examples, we don't use "set" methods since
   # they're not idiomatic in Python; they appear here just to emphasize how
   # expressive a pointcut definition can be
   targets = [method for method in all_methods(
                 *[class_ for class_ in all_classes(sample_classes)
                   if issubclass(class_, sample_classes.Shape)
                      or issubclass(class_, sample_classes.Canvas)])
              if method.__name__.startswith("set") or method.__name__.startswith("move")]
   def after_advice(self, retval, *args, **kwargs):
      redraw(self.core_callable, args[0]) # in methods, args[0] === self
      
class CorrectObserverAspect(CFlowBase):
   targets = [method for method in all_methods(
                 *[class_ for class_ in all_classes(sample_classes)
                   if issubclass(class_, sample_classes.Shape)
                      or issubclass(class_, sample_classes.Canvas)])
              if method.__name__.startswith("set") or method.__name__.startswith("move")]
   def after_advice(self, retval, *args, **kwargs):
      redraw(self.core_callable, args[0])


      
class TraceAspect(DepthBase):
   # Extensional definition; more localized than using decorators, but not any
   # more expressive. If you forget to include a method (or if you forget to
   # tag a method with a decorator when it really needs one) your mistake will
   # lurk quietly in the background until something goes wrong.
   targets = [sample_classes.Shape.move_by,
              sample_classes.Canvas.__init__,
              sample_classes.Canvas.move_by,
              sample_classes.Polygon.__init__,
              sample_classes.Polygon.move_by,
              sample_classes.Line.__init__,
              sample_classes.Line.move_by,
              sample_classes.Point.__init__,
              sample_classes.Point.move_by,
             ]

   # Intensional definition; evolves with the program when new classes or
   # methods are added
   targets = all_methods(*all_classes(sample_classes))
   
   def before_advice(self, *args, **kwargs):
      print("--"*(self.depth+1)+">", "core_callable:", self.core_callable)
      print("  "*(self.depth+1)+" ", "args:", args)
      print("  "*(self.depth+1)+" ", "kwargs:", kwargs)
   def after_advice(self, retval, *args, **kwargs):
      print("<"+"--"*(self.depth+1), "core_callable:", self.core_callable)
      print(" "+"  "*(self.depth+1), "retval:", retval)
      print(" "+"  "*(self.depth+1), "args:", args)
   def after_exception_advice(self, exception, *args, **kwargs):
      print("<"+"xx"*(self.depth+1), "core_callable:", self.core_callable)
      print(" "+"  "*(self.depth+1), "exception:", exception)



class LawOfDemeterChecker(DepthBase):
   '''
   Aspect for checking whether an OO design conforms to the Law of Demeter.
   Inspired by "A Case for Statically Executable Advice: Checking the Law of
   Demeter with AspectJ*" [Lieberherr, Lorenz, Hu 2003]

   Wikipedia says [http://en.wikipedia.org/wiki/Law_Of_Demeter]:
   "... the Law of Demeter for functions requires that a method m of an object O
   may only invoke the methods of the following kinds of objects:

   O itself
   m's parameters
   Any objects created/instantiated within m
   O's direct component objects
   A global variable, accessible by O, in the scope of m"

   I would add another condition specific to Python: "Members of sequences that
   are direct component objects of O".
   In Python, we tend to treat sequences casually in terms of encapsulation --
   when an object "knows" about its own attributes, it generally "knows" about
   the contents of its sequence attributes in the same way. But if you have
   attributes that are lists of lists... well, I don't do much Python programing
   anymore anyway so I'll just let you judge for yourself whether that's an
   acceptable design decision.
   '''
   module = sample_classes
   targets = all_methods(*all_classes(module))
   call_stack = []

   def depth_print(self, *args):
      print("  "*(self.depth+1)+" ", *args)

   def is_in_sequence_attribute(self, caller):
      for attr in self.call_stack[-1]["caller"].__dict__.values():
         if isinstance(attr, collections.Iterable) and caller in attr:
            return True
      return False

   def before_advice(self, *args, **kwargs):
      caller = args[0]
      method_args = args[1:]
      if len(self.call_stack) > 0:
         if caller is self.call_stack[-1]["caller"]:
            # "O itself"
            self.depth_print("method call acceptable:",
                             caller,
                             "is previous self arg")
         elif caller in self.call_stack[-1]["arguments"]:
            # "m's parameters"
            self.depth_print("method call acceptable:",
                             caller,
                             "passed as argument to previous method")
         elif caller in self.call_stack[-1]["instantiatees"]:
            # "Any objects created/instantiated within m"
            self.depth_print("method call acceptable:",
                             caller,
                             "created within previous method")
         elif caller in self.call_stack[-1]["caller"].__dict__.values():
            # "O's direct component objects"
            self.depth_print("method call acceptable:",
                             caller,
                             "is attribute of previous caller")
         elif caller in self.module.__dict__.items():
            # "A global variable, accessible by O, in the scope of m"
            self.depth_print("method call acceptable:",
                             caller,
                             "is global in module",
                             self.module)
         elif self.is_in_sequence_attribute(caller):
            self.depth_print("method call acceptable:",
                             caller,
                             "is member of iterable attribute of previous caller")
         elif self.core_callable.__name__ == "__init__":
            self.depth_print("method call acceptable: init method")
         else:
            print("xx"*(self.depth+1)+" ",
                  "method call UNACCEPTABLE:",
                  caller,
                  "is not a friend of previous method")
      else:
         self.depth_print("method call acceptable:",
                          caller,
                          "called at top level")
      #call_info = [caller, list(method_args) + kwargs.values(), []]
      call_info = {"caller":caller,
                   "arguments":list(method_args) + kwargs.values(),
                   "instantiatees":[]}
      self.__class__.call_stack.append(call_info)
   def after_advice(self, retval, *args, **kwargs):
      self.call_stack.pop()
      if self.core_callable.__name__ == "__init__" and len(self.call_stack) > 0:
         # This case is handled somewhat differently. When a new object is
         # instantiated within a method, it should be allowed as an argument to
         # subsequent method calls, but we don't know how to identify it until
         # after it's been instantiated. No object can be used without first
         # being instantiated, so we can simply wrap __init__ methods with an
         # instruction to add the newly created object to a list of LOD-approved
         # objects for the parent method invocation
         self.call_stack[-1]["instantiatees"].append(args[0])
   def after_exception_advice(self, exception, *args, **kwargs):
      self.call_stack.pop()
      if self.core_callable.__name__ == "__init__" and len(self.call_stack) > 0:
         # same as after_advice
         #self.call_stack[-1][2].append(args[0])
         self.call_stack[-1]["instantiatees"].append(args[0])




active_debug_aspects = (LawOfDemeterChecker,
                        #TraceAspect,
                        )

production_aspects = (#IncorrectObserverAspect,
                      CorrectObserverAspect,
                      )
