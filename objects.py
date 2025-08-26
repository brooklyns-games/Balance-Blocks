"""Balance Blocks
A logic-based puzzle game
You are given blocks of identical volume
And you have to rank their masses
You can use the set of scales to find the relative mass

"""
import pygame
import pymunk

from pymunk import Vec2d

from abc import ABC, abstractmethod

import global_vars
from global_vars import clear_surface
from constraints import *

def transform(x, y, vertices):
    # Transform the vertices to world coordinates
    transformed_vertices = []
    for v in vertices:
        # print(v)
        # print(pymunk.Vec2d(x, y), pymunk.Vec2d(*v))
        tv = v + pymunk.Vec2d(x, y)
        # print(tv)
        transformed_vertices.append(tv)
    return transformed_vertices

def get_rect(shape):
    # from https://www.google.com/search?q=pymunk+get+rect+from+shape&rlz=1C5CHFA_enUS954US954&oq=pymunk+get+rect+from+shape&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQIRigATIHCAIQIRigATIHCAMQIRigATIHCAQQIRiPAtIBCDQwMDJqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8
    body = shape.body

    if isinstance(shape, pymunk.Poly):
        vertices = shape.get_vertices()
    elif isinstance(shape, pymunk.Circle):
        r = shape.radius
        vertices = [(-r, r), (r, r), (-r, -r), (r, -r)]
    elif isinstance(shape, pymunk.Segment):
        vertices = [shape.a, shape.b]
    else:
        return None  # Handle other shape types if needed
    # print(body.position)
    transformed_vertices = transform(*body.position, vertices)

    # Calculate the bounding box
    min_x = min(v.x for v in transformed_vertices)
    max_x = max(v.x for v in transformed_vertices)
    min_y = min(v.y for v in transformed_vertices)
    max_y = max(v.y for v in transformed_vertices)

    return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

clickables = pygame.sprite.Group() # sprites that can be interacted with by mouse

class BodySprite(pygame.sprite.Sprite, ABC):
    siblings = pygame.sprite.Group()
    def __init__(self, x, y, mass=10,
                 body_type=pymunk.Body.DYNAMIC,
                 clickable: bool=False, **kwargs):
        """
        Base class for objects to add into the simulation. Most of these params are just pymunk.Body attrs
        :param x: body x-coord
        :param y: body y-coord
        :param color: Not implemented, go away
        :param clickable: able to be clicked, dragged, and dropped by mouse
        """
        super().__init__(global_vars.BODIES, self.__class__.siblings)
        if clickable:
            self.add(clickables)

        self.color = kwargs.get('color', (255, 0, 0, 255))
        self.mass = mass

        self.body = pymunk.Body(mass=self.mass, moment=1, body_type=body_type)
        self.body.position = self.x, self.y = x, y

        self.shape = self.set_shape()  # pymunk.Poly(self.body, [(-1, 1), (1, 1), (1, -1), (-1, -1)])
        self.shape = self.initialize_shape(self.shape)
        self.shape.collision_type = kwargs.get('collision_type', 0)
        self.shape.filter = pymunk.ShapeFilter(categories=kwargs.get('category', 0), mask=kwargs.get('mask', 0))

        self.rect = pygame.Rect(self.x, self.y, self.mass * 10, self.mass * 10)
        # self.image = clear_surface(*self.rect.size)



        SPACE.add(self.body, self.shape)
        # print('added', self.body, self.shape)
        self.update()

    @staticmethod
    def initialize_shape(shape):
        # Keep density at 0 so Body.mass/moment are not auto-overridden by shape density.
        # This ensures the explicit mass set on the Body is respected.
        shape.density = 1
        shape.friction = 1
        shape.collision_slop = 0
        return shape

    def rect_update(self):
        self.rect.update(*get_rect(self.shape))
        return self.rect

    @abstractmethod
    def set_shape(self):
        return pymunk.Circle(self.body, 10)

    def update(self):  # find way to put this in all children's update methods
        # self.body.moment =0
        # if self.body.body_type == pymunk.Body.DYNAMIC:
        #     self.body.mass = self.m

        # print('updating', self.body, self.body.position, self.shape)
        self.x, self.y = self.body.position
        self.rect_update()
        # print('updating', self.body, self.body.position, self.shape)
        # assert self.body.mass > 0, "Mass must be positive and non-zero"
        # self.image = clear_surface(*self.rect.size)

    def draw(self, s):
        pass
        # pygame.draw.rect(s, self.color, self.rect_update())


class Ball(BodySprite):
    def __init__(self, x, y, r, **kwargs):
        """Boing..."""
        self.radius = r
        super().__init__(x, y, 5, kwargs.get('collision_type'), kwargs.get('color'))
        # self.body.velocity = random.uniform(-500, 500), random.uniform(-500, 500)
        self.h, self.w = self.radius * 2, self.radius * 2

        self.shape.elasticity = 1



    def set_shape(self):
        return pymunk.Circle(self.body, self.radius)

    def draw(self, s):
        pygame.draw.circle(s, self.color, (self.x, self.y), self.radius)


class Box(pygame.sprite.Sprite):
    def __init__(self, p0=(0, 0), p1=(W, H), d=4, **kwargs):
        super().__init__()
        """
        Makes an empty box with four walls, used to keep objects inside window
        *Does not add to bodies sprite group
        :param p0: top left corner
        :param p1: bottom right corner
        :param d: radius of walls
        """
        x0, y0 = p0
        x1, y1 = p1
        vs = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            seg = pymunk.Segment(
                b0, vs[i], vs[(i + 1) % 4], d, )
            seg.elasticity = 1
            seg.friction = 0.5
            seg.filter = pymunk.ShapeFilter(categories=kwargs.get('category', 0), mask=kwargs.get('mask', 0))
            # seg.color = color
            SPACE.add(seg)


class Block(BodySprite):
    def __init__(self, x, y, m, **kwargs):
        """
        A square or rectangle that can be dragged around, etc
        """
        self.size = self.w, self.h = kwargs.get('size', (40, 40))
        super().__init__(x, y, m, **kwargs, clickable=True, body_type=pymunk.Body.DYNAMIC)
        self.add(global_vars.BLOCKS)

        self.shape.elasticity = 0
        self.shape.friction = 100000

    def set_shape(self):
        return pymunk.Poly.create_box(self.body, self.size)

    def touching(self, arbiter, space, data):
        # print('yeet!')
        # self.body.velocity = Vec2d(0, 0)
        # self.body.velocity = (0, 0)
        return True

class Triangle(BodySprite):
    def __init__(self, x, y, l, **kwargs):
        self.l = l
        super().__init__(x, y, **kwargs)


    def set_shape(self):
        return pymunk.Poly(self.body, [(self.l, self.l), (-self.l, self.l), (0, 0)])


class Segment(BodySprite):
    def __init__(self, p0, v, r=10, m=20, center=False, damp=False, **kwargs):
        self.v = v
        self.r = r
        self.center = center
        self.damp = damp

        # mid = p0 + v * 0.5
        super().__init__(*p0 if not self.center else (p0 + v * 0.5), mass=m,
                         **kwargs)
        # self.body.position = p0  # Set the body's position to the start point
        self.shape.elasticity = 0.5

    def set_shape(self):
        # Always create the segment from (0, 0) to self.v in local coordinates
        if not self.center:
            return pymunk.Segment(self.body, (0, 0), self.v, self.r)
        else:
            return pymunk.Segment(self.body, -0.5 * self.v, 0.5 * self.v, self.r)

    def update(self):
        super().update()
    #     # self.body.moment = pymunk.moment_for_segment(self.mass, (0, 0), self.v, self.r)
    #     print('\tsegment', self.body)
    #
        if self.damp:
            self.body.angle = 0
            self.body.angular_velocity *= 0.1

    def draw(self, s):
        pygame.draw.line(s, self.color,
                         (self.x, self.y), pymunk.Vec2d(self.x, self.y) + self.v,
                         self.r)


class LoadingPlatform(Segment):
    def __init__(self, p0, v, **kwargs):
        super().__init__(p0, v, **kwargs, body_type=pymunk.Body.STATIC)
        self.has_block = False
        self.met = False  # None = never touched, True = correct block, False = wrong block

    def block_collide(self, arbiter, space, data):
        self.has_block = True
        return True
    def block_separated(self, arbiter, space, data):
        self.has_block = False
        return True

    def correct_block_collide(self, arbiter, space, data):

        self.met = True
        # print('hi!', self.met)
        return True

    def correct_block_separated(self, arbiter, space, data):
        self.met = False
        # print('bye!', self.met)
        return True

class LoadingBox(pygame.sprite.Sprite):
    def __init__(self, p0, p1, **kwargs):
        super().__init__()
        """
        Makes an empty box with four walls, used to keep objects inside window
        *Does not add to bodies sprite group
        :param p0: top left corner
        :param p1: bottom right corner
        :param d: radius of walls
        """
        x0, y0 = p0
        x1, y1 = p1
        self.vs = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

            # seg.color = color
            # SPACE.add(seg)
    def draw(self, screen):
        for i in range(4):
            plat = (self.vs[i], pymunk.Vec2d(*(self.vs[(i + 1) % 4]) - pymunk.Vec2d(*self.vs[i])),)


class Seesaw:
    def __init__(self, center: tuple, beam_length: "Vec2d|tuple", carrier_length: "Vec2d|tuple"):

        p = Vec2d(*center)
        v = Vec2d(*beam_length)
        v2 = Vec2d(*carrier_length)

        self.beam = Segment(p, v, category=1, mask=16, center=True)
        # self.beam.shape.damping = 0.9
        mid_local = Vec2d(*float_to_int((0.5 * v)))
        mid_world = float_to_int(p + mid_local)  # Attach only at the middle
        PivotJoint(b0, self.beam.body, mid_world, (0, 0), collide=False)
        #
        # carriers
        self.carrier1 = Deck(p - 0.5 * v2, v2)
        PivotJoint(self.carrier1.body, self.beam.body, v2 * 0.5, v * -0.5)

        self.carrier2 = Deck(p + v - v2 * 0.5, v2)
        PivotJoint(self.carrier2.body, self.beam.body, v2 * 0.5, v * 0.5)

        self.fulcrum = Triangle(*mid_world, 50, category=8, mask=1, body_type=pymunk.Body.STATIC)


class Deck(Segment, pygame.sprite.Sprite):
    decks = []
    def __init__(self, p0, v):
        self.loaded = []
        self.load = 0
        # self.load = pygame.sprite.GroupSingle()
        super().__init__(p0, v, m=100, damp=True, category=2, mask=20, collision_type=len(Deck.decks),
                         )  # body_type=pymunk.Body.KINEMATIC
        Deck.decks.append(self)

