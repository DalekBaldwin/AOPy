from __future__ import print_function
from contextlib import contextmanager
from functools import wraps

# For comparison, an implementation of the top-level change observer with
# decorators. This is probably a clean enough alternative for production
# aspects that are not likely to be changed, but decorators quickly become
# tiring when it comes to debugging

def observer(f):
   @wraps(f)
   def wrapper(*args, **kwargs):
      global pending_update
      oldvalue = pending_update
      pending_update = True
      try:
         result = f(*args, **kwargs)
      finally:
         pending_update = oldvalue
         if not pending_update:
            redraw()
      return result
   return wrapper

pending_update = False

def redraw():
   print("redrawing the screen")


   
class Shape(object):
   def move_by(self, dx, dy):
      pass

class Canvas(object):
   def __init__(self, shapes):
      self.shapes = shapes

   @observer
   def move_by(self, dx, dy):
      for shape in self.shapes:
            shape.move_by(dx, dy)

class Polygon(Shape):
   def __init__(self, lines):
      self.lines = lines

   @observer
   def move_by(self, dx, dy):
      for line in self.lines:
         line.move_by(dx, dy)
      
class Line(Shape):
   def __init__(self, p1, p2):
      self.p1 = p1
      self.p2 = p2

   @observer
   def move_by(self, dx, dy):
      self.p1.move_by(dx, dy)
      self.p2.move_by(dx, dy)

class Point(Shape):
   def __init__(self, x, y):
      self.x = x
      self.y = y

   @observer
   def move_by(self, dx, dy):
      self.x += dx
      self.y += dy
