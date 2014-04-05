from __future__ import print_function
from contextlib import contextmanager
from functools import wraps

# For comparison, an implementation of the top-level change observer with
# explicit context management

@contextmanager
def let(place, value):
   oldvalue = place.value
   place.value = value
   yield
   place.value = oldvalue

class Container(object):
   def __init__(self, value):
      self.value = value

pending_update = Container(False)

def redraw():
   print("redrawing the screen")


   
class Shape(object):
   def move_by(self, dx, dy):
      pass

class Canvas(object):
   def __init__(self, shapes):
      self.shapes = shapes

   def move_by(self, dx, dy):
      with let(pending_update, True):
         for shape in self.shapes:
            shape.move_by(dx, dy)
      if not pending_update.value:
         redraw()

class Polygon(Shape):
   def __init__(self, lines):
      self.lines = lines

   def move_by(self, dx, dy):
      with let(pending_update, True):
         for line in self.lines:
            line.move_by(dx, dy)
      if not pending_update.value:
         redraw()

class Line(Shape):
   def __init__(self, p1, p2):
      self.p1 = p1
      self.p2 = p2

   def move_by(self, dx, dy):
      with let(pending_update, True):
         self.p1.move_by(dx, dy)
         self.p2.move_by(dx, dy)
      if not pending_update.value:
         redraw()

class Point(Shape):
   def __init__(self, x, y):
      self.x = x
      self.y = y

   def move_by(self, dx, dy):
      self.x += dx
      self.y += dy
      if not pending_update.value:
         redraw()
