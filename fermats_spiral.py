# A way of most evenly distributing N points on a circle
# https://en.wikipedia.org/wiki/Fermat%27s_spiral

import turtle
from math import sin, cos, pi, sqrt, log, log2, atan2, ceil, e

SAMPLE_COUNT = 256
OUTER_RADIUS = 512

GOLDEN_ANGLE = 2.39996322973
DOT_RADIUS = sqrt(OUTER_RADIUS * OUTER_RADIUS / SAMPLE_COUNT)

turtle.color("blue")
turtle.dot(OUTER_RADIUS * 2)
turtle.speed(0)
turtle.color("black")

for i in range(SAMPLE_COUNT):
	r = sqrt(i / SAMPLE_COUNT) * OUTER_RADIUS
	x = r * cos(i * GOLDEN_ANGLE)
	y = r * sin(i * GOLDEN_ANGLE)
	turtle.goto(x, y)
	turtle.dot(DOT_RADIUS * 2, "red")

turtle.done()
