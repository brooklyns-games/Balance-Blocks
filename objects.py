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
    def __init__(self, x, y, mass=0, collision_type=0, category=0, mask=100, color=(255, 0, 0, 255),
                 body_type=pymunk.Body.DYNAMIC, clickable: bool=False):
        """
        Base class for objects to add into the simulation. Most of these params are just pymunk.Body attrs
        :param x: body x-coord
        :param y: body y-coord
        :param color: Not implemented, go away
        :param clickable: able to be clicked, dragged, and dropped by mouse
        """
        super().__init__(global_vars.bodies, self.__class__.siblings)
        if clickable:
            self.add(clickables)

        self.color = color

        self.m = mass
        self.body = pymunk.Body(self.m, body_type=body_type, moment=0)
        self.body.position = self.x, self.y = x, y

        self.shape = self.set_shape()  # pymunk.Poly(self.body, [(-1, 1), (1, 1), (1, -1), (-1, -1)])
        self.shape.density = 1
        self.shape.friction = 1

        self.shape.collision_type = collision_type
        self.shape.filter = pymunk.ShapeFilter(categories=category, mask=mask)

        self.rect = pygame.Rect(self.x, self.y, self.m * 10, self.m * 10)
        self.image = clear_surface(*self.rect.size)

        self.update()

    def rect_update(self):
        self.rect.update(*get_rect(self.shape))
        return self.rect

    @abstractmethod
    def set_shape(self):
        return pymunk.Circle(self.body, 10)

    def update(self):  # find way to put this in all children's update methods
        self.x, self.y = self.body.position
        self.rect_update()
        self.image = clear_surface(*self.rect.size)

    def draw(self, s):
        pygame.draw.rect(s, self.color, self.rect_update())


class Ball(BodySprite):
    def __init__(self, x, y, r, collision_type=0, group=0, color=(255, 0, 0)):
        """Boing..."""
        self.radius = r
        super().__init__(x, y, 5, collision_type, color=color)
        # self.body.velocity = random.uniform(-500, 500), random.uniform(-500, 500)
        self.h, self.w = self.radius * 2, self.radius * 2

        self.shape.elasticity = 1

        self.shape.filter = pymunk.ShapeFilter(group=group)

    def set_shape(self):
        return pymunk.Circle(self.body, self.radius)

    def draw(self, s):
        pygame.draw.circle(s, self.color, (self.x, self.y), self.radius)


class Box:
    def __init__(self, p0=(0, 0), p1=(W, H), d=4, color=(255, 0, 0), category=0, mask=0):
        """
        Makes an empty box with four walls, used to keep objects inside window
        *Does not add to bodies sprite group
        :param p0: top left corner
        :param p1: bottom right corner
        :param d: radius?
        :param color:
        :param category:
        :param mask:
        """
        x0, y0 = p0
        x1, y1 = p1
        vs = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            seg = pymunk.Segment(
                SPACE.static_body, vs[i], vs[(i + 1) % 4], d)
            seg.elasticity = 1
            seg.friction = 0.5
            seg.filter = pymunk.ShapeFilter(categories=category, mask=mask)
            # seg.color = color
            SPACE.add(seg)


class Block(BodySprite):
    def __init__(self, x, y, size=(40, 40), m=10, color=(255, 0, 0), clickable=False,
                 collision_type=0, category=0, mask=0, body_type=pymunk.Body.DYNAMIC):
        """
        A square or rectangle that can be dragged around, etc
        """
        self.size = self.w, self.h = size
        super().__init__(x, y, m, color=color, clickable=clickable,
                         collision_type=collision_type, category=category, mask=mask, body_type=body_type)
        self.add(global_vars.blocks)

        self.shape.elasticity = 0
        self.shape.friction = 10

    def set_shape(self):
        return pymunk.Poly.create_box(self.body, self.size)
    # def update(self):
    #     super().update()
        # print(self.rect)

class Triangle(BodySprite):
    def __init__(self, x, y, l, body_type=pymunk.Body.DYNAMIC, category=0, mask=0):
        self.l = l
        super().__init__(x, y, body_type=body_type, category=category, mask=mask)


    def set_shape(self):
        return pymunk.Poly(self.body, [(self.l, self.l), (-self.l, self.l), (0, 0)])


class Segment(BodySprite):
    def __init__(self, p0, v, r=10, color=(255, 0, 0), m=20, center=False, collision_type=0, category=0, mask=0,
                 body_type=pymunk.Body.DYNAMIC, damp=False):
        self.v = v
        self.r = r
        self.center = center
        self.damp = damp

        # mid = p0 + v * 0.5
        super().__init__(*p0 if not self.center else (p0 + v * 0.5), mass=m, body_type=body_type, color=color,
                         collision_type=collision_type, category=category, mask=mask)
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
        if self.damp:
            self.body.angle = 0
            self.body.angular_velocity *= 0.1
        # self.body.moment = self.moment

    def draw(self, s):
        pygame.draw.line(s, self.color,
                         (self.x, self.y), pymunk.Vec2d(self.x, self.y) + self.v,
                         self.r)


class LoadingPlatform(Segment):
    def __init__(self, p0, v,  collision_type=0, category=0, mask=0):
        super().__init__(p0, v, collision_type=collision_type,
                         category=category, mask=mask, body_type=pymunk.Body.STATIC)
        self.met = False

    def tagged(self, arbiter, space, data):
        # print('hi!')
        self.met = True
        return True

    def separated(self, arbiter, space, data):
        self.met = False
        return True


class Seesaw:
    def __init__(self, center, beam_length: Vec2d, carrier_length):
        b0 = SPACE.static_body

        p = Vec2d(*center)
        v = Vec2d(*beam_length)
        v2 = Vec2d(*carrier_length)

        self.beam = Segment(p, v, category=1, mask=16, body_type=pymunk.Body.KINEMATIC)
        mid_local = 0.5 * v
        mid_world = p + mid_local  # Attach only at the middle
        # PivotJoint(b0, self.beam.body, mid_world, mid_local, collide=False)

        # carriers
        self.carrier1 = Deck(p - v2 * 0.5, v2)
        PivotJoint(self.carrier1.body, self.beam.body, v2 * 0.5, (0, 0))

        # self.carrier2 = Deck(p + v - v2 * 0.5, v2)
        # PivotJoint(self.carrier2.body, self.beam.body, v2 * 0.5, v)
        #
        self.fulcrum = Triangle(*mid_world, 50, pymunk.Body.STATIC, category=8, mask=1)


        # j1 = pymunk.SlideJoint(self.carrier1.body, b0, (0, 0), (50, 400), 0, 100)
        # j2 = pymunk.SlideJoint(self.carrier1.body, b0, v2, (100, 400), 0, 100)
        # SPACE.add(j1)
    def update(self):
        pass
        # does not update, need to be child of BodySprite. oh well
        # print(pygame.sprite.spritecollideany(self.carrier1, global_vars.blocks))

class Deck(Segment, pygame.sprite.Sprite):
    decks = []
    def __init__(self, p0, v):
        self.loaded = 0
        super().__init__(p0, v, m=100, damp=True, category=2, mask=20, collision_type=len(Deck.decks))
        Deck.decks.append(self)


    def touching(self, arbiter, space, data):
        # self.loaded.add(sprite)
        self.loaded += 1
        print('touching', pygame.sprite.spritecollideany(self, global_vars.blocks))
        return True
    def separated(self, arbiter, space, data):
        # self.loaded.remove(sprite)
        self.loaded -= 1
        print('separated')
        return True
    def update(self):
        super().update()
        for b in global_vars.blocks:
            print('\t', self.shape.shapes_collide(b.shape))
        # print(self, self.loaded)
        # print(self.rect)
    #     # print(global_vars.level_num)

    #     print(pygame.sprite.spritecollideany(self, global_vars.blocks))
        if pygame.sprite.spritecollideany(self, global_vars.blocks):
    #         # pass
            print('hi')

