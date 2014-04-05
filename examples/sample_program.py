#!/usr/bin/env python

'''
This is based on the classic figure-editor example from AspectJ.

When using an observer aspect derived from ExecutionBase, we erroneously trigger
multiple screen redraws before the entire data model has been updated. Simply by
deriving from CFlowBase instead, we ensure that the redraw does not occur until
the topmost invocation of move_by returns. Go into sample_aspects.py and change
production_aspects to see this.

With this project structure, we can seamlessly introduce aspects for debugging
as well. Run this file as "python sample_program.py -d" to see.
'''

from __future__ import print_function
from sample_classes import Canvas, Polygon, Line, Point
#from sample_classes_tangled import Canvas, Polygon, Line, Point
#from sample_classes_decorator import Canvas, Polygon, Line, Point
from sample_aspects import active_debug_aspects, production_aspects

import argparse
parser = argparse.ArgumentParser(description="Test some aspects!")
parser.add_argument("-d", dest="debug", action="store_const",
                    const=True, default=False,
                    help="Print verbose debugging output.")
args = parser.parse_args()


for aspect in production_aspects:
   aspect.enable()

if args.debug:
   for aspect in active_debug_aspects:
      aspect.enable()


square = Polygon([Line(Point(1,1), Point(1,4)),
                  Line(Point(1,4), Point(4,4)),
                  Line(Point(4,4), Point(4,1)),
                  Line(Point(4,1), Point(1,1))])
line = Line(Point(5,2), Point(6,5))
point = Point(8,9)
canvas = Canvas([square, line, point])

print("About to move a single point.")
point.move_by(0,1)
print("")

print("About to move a line containing points.")
line.move_by(2,3)
print("")

print("About to move a shape containing lines containing points.")
square.move_by(4,5)
print("")

print("About to move a canvas containing shapes containing lines containing points.")
canvas.move_by(6,7)
