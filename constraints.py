import pygame
import pymunk

from global_vars import *

class PivotJoint:
    def __init__(self, b, b2, a=(0, 0), a2=(0, 0), collide=False):

        self.joint = pymunk.PivotJoint(b, b2, a, a2)
        self.joint.collide_bodies = collide
        SPACE.add(self.joint)


class PinJoint:
    def __init__(self, b, b2, a=(0, 0), a2=(0, 0), collide=False):
        self.joint = pymunk.PinJoint(b, b2, a, a2)
        self.joint.collide_bodies = collide
        SPACE.add(self.joint)


class DampedRotarySpring:
    def __init__(self, a, b, angle, stiffness, damping):
        self.joint = pymunk.DampedRotarySpring(a, b, angle, stiffness, damping)
        SPACE.add(self.joint)

