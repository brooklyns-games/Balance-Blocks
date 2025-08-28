"""Balance Blocks
A logic-based puzzle game
You are given blocks of identical volume
And you have to rank their masses
You can use the set of scales to find the relative mass

"""
from typing import Tuple

import pygame
import pymunk




from global_vars import *
from constraints import *
from interface import GameObject, ClickableSprite


def bb_to_rect(bb: pymunk.BB):
    l, b, r, t = bb
    return  pygame.Rect(int(l), int(H - t), int(r - l), int(t - b))

def transform(body, vertices):
    # Transform local vertices to world coordinates, including rotation
    transformed_vertices = []
    angle = body.angle
    pos = pymunk.Vec2d(*body.position)
    for v in vertices:
        tv = v.rotated(angle) + pos
        transformed_vertices.append(tv)
    return transformed_vertices

def get_vertices(shape) -> "list[Tuple[float, float]]|list[pymunk.Vec2d]":
    if isinstance(shape, pymunk.Poly):
        vertices = shape.get_vertices()
    elif isinstance(shape, pymunk.Circle):
        r = shape.radius
        vertices = [(-r, r), (r, r), (-r, -r), (r, -r)]
    elif isinstance(shape, pymunk.Segment):
        vertices = [shape.a, shape.b]
    else:
        return []  # Handle other shape types if needed
    return vertices
    # print(body.position)


def get_rect(shape):
    # from https://www.google.com/search?q=pymunk+get+rect+from+shape&rlz=1C5CHFA_enUS954US954&oq=pymunk+get+rect+from+shape&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQIRigATIHCAIQIRigATIHCAMQIRigATIHCAQQIRiPAtIBCDQwMDJqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8
    body = shape.body
    transformed_vertices = transform(body, get_vertices(shape))



    # Calculate the bounding box
    min_x = min(v.x for v in transformed_vertices)
    max_x = max(v.x for v in transformed_vertices)
    min_y = min(v.y for v in transformed_vertices)
    max_y = max(v.y for v in transformed_vertices)

    return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)



class BodySprite(pygame.sprite.Sprite, ABC):
    siblings = pygame.sprite.Group()
    def __init__(self, x, y, mass=10, body_type=pymunk.Body.DYNAMIC, clickable: bool=False, **kwargs):
        """
        Base class for objects to add into the simulation. Has a pymunk body, shape
        :param x: body x-coord
        :param y: body y-coord
        :param color: for easier developer debugging
        :param clickable: able to be clicked, dragged, and dropped by mouse
        """
        super().__init__(BODIES, self.__class__.siblings)


        # if clickable:
        #     self.add(clickables)

        self.color = kwargs.get('color', (255, 0, 0, 255))
        self.mass = mass

        self.body = pymunk.Body(mass=self.mass, moment=1, body_type=body_type)
        self.body.position = self.x, self.y = x, y

        self.shapes = []
        self.shape = self.set_shape()  # pymunk.Poly(self.body, [(-1, 1), (1, 1), (1, -1), (-1, -1)])
        self.shape = self.initialize_shape(self.shape)
        self.shape.collision_type = kwargs.get('collision_type', 0)
        self.shape.filter = pymunk.ShapeFilter(categories=kwargs.get('category', 0), mask=kwargs.get('mask', 0))

        # self.rect = pygame.Rect(self.x, self.y, self.mass * 10, self.mass * 10)
        # self.image = clear_surface(*self.rect.size)
        # print(self.x, self.y)
        # print(bb_to_rect(pymunk.Poly(self.body, list(get_vertices(self.shape))).bb))
        # print(get_rect(self.shape))
        rect = get_rect(self.shape)
        self.game_sprite = GameObject(x = rect.left, y=rect.top, size=rect.size,
                                      color=self.color, )
        self.game_sprite.add(physics_sprites)
        # self.image = pygame.Surface([10, 10], pygame.SRCALPHA)

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
        # self.rect.update (*get_rect(self.shape))
        # temp_shape = pymunk.Poly(self.body, self.shape.vertices)
        bb = self.shape.cache_bb()
        # print(self.rect)


        # print(self.rect.topleft, bb.top, bb.left)
        # print(self.shape.bb.area())
        # print('\t', self.rect.size[0] * self.rect.size[1])
        # self.rect.topleft = flip(*self.rect.topleft)
        # self.rect.topleft = self.rect.bottomleft
        # return self.rect

    @abstractmethod
    def set_shape(self):
        return pymunk.Circle(self.body, 10)

    def update(self):  # find way to put this in all children's update methods
        self.x, self.y = self.body.position

        self.game_sprite.rotate(self.body.angle, self.x, self.y)
    def destroy(self):
        SPACE.remove(self.body, self.shape)
        self.game_sprite.kill()
        self.kill()


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


class Block(BodySprite, ClickableSprite):
    def __init__(self, x, y, m, **kwargs):
        """
        A square or rectangle that can be dragged around, etc
        """
        self.size = self.w, self.h = kwargs.get('size', (40, 40))
        super().__init__(x, y, m, **kwargs, clickable=True, body_type=pymunk.Body.DYNAMIC, color='blue')
        ClickableSprite.__init__(self)
        self.add(BLOCKS)

        self.shape.elasticity = 0
        self.shape.friction = 100000

        self.loaded = False

    def detect_hover(self):
        return self.shape.point_query(pygame.mouse.get_pos()).distance <= 0
    def click(self):
        clicked.sprite.snap_to_position(pygame.mouse.get_pos())
        # clicked.sprite.update()
    def drop(self):
        clicked.sprite.body.body_type = pymunk.Body.DYNAMIC


    def set_shape(self):
        return pymunk.Poly.create_box(self.body, self.size)

    def touching_deck(self, arbiter, space, data):
        # self.body.velocity *= 0.9
        self.body.velocity = (0, 0)
        self.body.angle = 0
        self.body.angular_velocity = 0

        return True
    def snap_to_position(self, pos):
        self.body.body_type = pymunk.Body.KINEMATIC
        self.body.position = pos
    def update(self):
        super().update()

        for loading_box in LoadingBox.loading_boxes:
            if pygame.sprite.collide_rect(self.game_sprite, loading_box.game_sprite):

                self.body.angle = 0
                self.snap_to_position(loading_box.game_sprite.rect.center)
                loading_box.block.add(self)
                break
            else:
                if loading_box.block.sprite == self:
                    loading_box.block.empty()

class Bracket:
    def __init__(self, p, length1, length2, r=5,):
        self.p = self.x, self.y = p
        self.v1 = length1
        self.v2 = length2
        self.r = r
        self.body = pymunk.Body()
        self.body.position = self.p

        self.s1 = pymunk.Segment(self.body, (0, 0), self.v1, self.r)
        self.s2 = pymunk.Segment(self.body, (0, 0), self.v2, self.r)
        self.s1.density = 1
        self.s2.density = 1
        SPACE.add(self.body, self.s1, self.s2)




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
                         **kwargs, color='green')
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
            self.body.angular_velocity = 0

    def draw(self, s):
        pygame.draw.line(s, self.color,
                         (self.x, self.y), pymunk.Vec2d(self.x, self.y) + self.v,
                         self.r)

class LoadingBox(BodySprite):
    loading_boxes = pygame.sprite.Group()
    def __init__(self, p0, size, target_weight, collision_type, **kwargs):

        """
        Makes an empty box with four walls, used to keep objects inside window
        *Does not add to bodies sprite group
        :param p0: top left corner
        :param size: bottom right corner
        :param d: radius of walls
        """
        x0, y0 = p0
        # x1, y1 = x0 + size[0], y0 + size[1]
        self.size = size
        super().__init__(x=x0, y=y0, **kwargs, color='red', body_type=pymunk.Body.STATIC)

        self.add(LoadingBox.loading_boxes)

        self.shape.sensor = True

        self.block = pygame.sprite.GroupSingle()
        self.target_weight = target_weight


    def set_shape(self):
        return pymunk.Poly.create_box(self.body, self.size)

    # def draw(self):
    #     super().draw()
    #     # print(self.rect)
    #     pygame.draw.rect(self.image, 'red', self.rect.inflate(-20, -20), 5)
    #     # for i in range(4):
    #         # pygame.draw.line(self.image, 'black', self.vs[i], self.vs[(i + 1) % 4], width=15)
    # # def update(self):
    # def update(self):
    #     super().update()
    #     # print(self.block)


class Deck(Segment, pygame.sprite.Sprite):
    decks = []
    def __init__(self, p0, v):
        self.loaded = []
        self.load = 0
        # self.load = pygame.sprite.GroupSingle()
        super().__init__(p0, v, m=100, damp=True, category=2, mask=20, collision_type=len(Deck.decks),
                         )  # body_type=pymunk.Body.KINEMATIC
        self.shape.friction = 100000
        Deck.decks.append(self)

