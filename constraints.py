import pygame
import pymunk

from global_vars import *

class PivotJoint(pygame.sprite.Sprite):
    def __init__(self, b, b2, a=(0, 0), a2=(0, 0), collide=False):

        self.joint = pymunk.PivotJoint(b, b2, a, a2)
        self.joint.collide_bodies = collide
        super().__init__(joints)


class PinJoint(pygame.sprite.Sprite):
    def __init__(self, b, b2, a=(0, 0), a2=(0, 0), collide=False):
        self.joint = pymunk.PinJoint(b, b2, a, a2)
        self.joint.collide_bodies = collide
        # SPACE.add(self.joint)
        super().__init__(joints)



class DampedRotarySpring:
    def __init__(self, a, b, angle, stiffness, damping):
        self.joint = pymunk.DampedRotarySpring(a, b, angle, stiffness, damping)
        SPACE.add(self.joint)

