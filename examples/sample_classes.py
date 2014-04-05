from __future__ import print_function

class Shape(object):
   def move_by(self, dx, dy):
      pass

class Canvas(object):
   def __init__(self, shapes = None):
      self.shapes = shapes or []

   def move_by(self, dx, dy):
      for shape in self.shapes:
         shape.move_by(dx, dy)

class Polygon(Shape):
   def __init__(self, lines = None):
      self.lines = lines or []

   def move_by(self, dx, dy):
      for line in self.lines:
         line.move_by(dx, dy)
      
class Line(Shape):
   def __init__(self, p1=None, p2=None):
      self.p1 = p1 or Point()
      self.p2 = p2 or Point()

   def move_by(self, dx, dy):
      self.p1.move_by(dx, dy)
      self.p2.move_by(dx, dy)

   # These can be used to more faithfully recreate the example from Java, but
   # this pattern is of course pretty useless in Python
   '''
   def setp1(self, p1):
      self.p1 = p1

   def setp2(self, p2):
      self.p2 = p2
   #'''

class Point(Shape):
   def __init__(self, x=0, y=0):
      self.x = x
      self.y = y

   def move_by(self, dx, dy):
      self.x += dx
      self.y += dy

   '''
   def setx(self, x):
      self.x = x

   def sety(self, y):
      self.y = y
   #'''
