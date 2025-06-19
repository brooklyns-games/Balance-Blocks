import random
import pygame
import pymunk
# print(pymunk.pygame_util)
from pymunk import Vec2d
from pymunk.pygame_util import DrawOptions

"""Started June 14 2025
from Pymunk Basics by Ear of Corn Programming
https://youtube.com/playlist?list=PL_N_kL9gRTm8lh7GxFHh3ym1RXi6I6c50&si=IqN679o1NsVTzN6q

"""


W, H = 800, 400
SPACE = pymunk.Space()
SPACE.gravity = (0, 1000)


def clear_surface(h, w, fill=None):
    if fill is None:
        return pygame.Surface((h, w), pygame.SRCALPHA)
    else:
        s = pygame.Surface((h, w))
        s.fill(fill)
        return s

def limit_velocity(body, gravity, damping, dt):
    """
    https://www.pymunk.org/en/latest/overview.html
    :param body:
    :param gravity
    :param damping
    :param dt
    :return:
    """
    max_velocity = 1000
    # pymunk.Body.update_velocity()

def flip(x, y, null=False, return_as=tuple):
    if not null:
        return return_as((x, H - y))
    else:
        return return_as((x, y))


def new_body_at(x=0, y=0, m=0, body_type=pymunk.Body.DYNAMIC, collision_type=0):
    b = pymunk.Body(m, body_type)
    b.position = flip(x, y)

    return b


bodies = pygame.sprite.Group()
joints = pygame.sprite.Group()


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


class BodySprite(pygame.sprite.Sprite):
    body_num = 0

    def __init__(self, x, y, mass=0, collision_type=0, category=0, mask=100, color=(255, 0, 0, 255),
                 body_type=pymunk.Body.DYNAMIC, clickable=False):
        super().__init__(bodies)
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

        # BodySprite.body_num += 1
        # self.shape.collision_type = collision_type  # BodySprite.body_num

    def set_shape(self):
        return pymunk.Circle(self.body, 10)

    def update(self):
        self.x, self.y = self.body.position
        # print(self.shape)
        # print(get_rect(self.shape))
        self.rect.update(*get_rect(self.shape))

    def draw(self, s):
        pygame.draw.rect(s, self.color, get_rect(self.shape))
        # pygame.draw.polygon(s, self.color, transform(self.x, self.y, self.shape.get_vertices()))


class Ball(BodySprite):
    def __init__(self, x, y, r, collision_type=0, group=0, color=(255, 0, 0)):
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
        # super().__init__(*p0, color=color, body_type=pymunk.Body.STATIC)
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


class Chassis(BodySprite):
    def __init__(self, x, y, vs):
        self.vertices = vs
        super().__init__(x, y, 10, )
        self.shape.filter = pymunk.ShapeFilter(group=1)

        # v0, v1, v2, v3 = self.vertices

        # self.shape = p
        # self.shape.density = 1

    def set_shape(self):
        return pymunk.Poly(self.body, self.vertices)

    # def draw(self, s):
    #     pygame.draw.polygon(s, self.color, self.vertices)


class Wheel(BodySprite):
    def __init__(self, x, y, r, chassis, a, group=1, speed=5):
        self.r = r
        super().__init__(x, y, 5)
        self.shape.filter = pymunk.ShapeFilter(group=group)

        self.joint = pymunk.PivotJoint(chassis.body, self.body, a, (0, 0))
        self.joint.collide_bodies = True

        self.motor = pymunk.SimpleMotor(chassis.body, self.body, speed)
        SPACE.add(self.joint, self.motor)

    def set_shape(self):
        return pymunk.Circle(self.body, self.r)

    def draw(self, s):
        pygame.draw.circle(s, self.color, self.body.position, self.r, 5)





def collide(arbiter, space, data):
    print('hello')
    return True


class Rope(pygame.sprite.Sprite):
    def __init__(self, body, attachment):
        super().__init__(joints)
        self.body1 = body
        if isinstance(attachment, pymunk.Body):
            self.body2 = attachment

        elif isinstance(attachment, tuple):
            self.body2 = pymunk.Body(body_type=pymunk.Body.STATIC)
            self.body2.position = flip(*attachment)
        self.joint = pymunk.PinJoint(self.body1, self.body2)
        # SPACE.add(self.joint)

        self.start = self.body1.position
        self.end = self.body2.position

    def update(self):
        self.start = self.body1.position
        self.end = self.body2.position

    def draw(self, s):
        pygame.draw.line(s, (0, 0, 0), self.start, self.end, 3)


class Block(BodySprite):
    def __init__(self, x, y, size=(40, 40), m=10, color=(255, 0, 0), clickable=False,
                 collision_type=0, category=0, mask=0, body_type=pymunk.Body.DYNAMIC):

        self.size = self.w, self.h = size
        super().__init__(x, y, m, color=color, clickable=clickable,
                         collision_type=collision_type, category=category, mask=mask, body_type=body_type)

        self.shape.elasticity = 0
        self.shape.friction = 0.5

    def set_shape(self):
        return pymunk.Poly.create_box(self.body, self.size)



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
        # self.shape.filter = pymunk.ShapeFilter(group=1)

    def set_shape(self):
        # Always create the segment from (0, 0) to self.v in local coordinates
        if not self.center:
            return pymunk.Segment(self.body, (0, 0), self.v, self.r)
        else:
            return pymunk.Segment(self.body, -0.5 * self.v, 0.5 * self.v, self.r)
    def update(self):
        BodySprite.update(self)
        if self.damp:
            self.body.angular_velocity *= 0.5
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
        print('hi!')
        self.met = True
        return True
    def separated(self, arbiter, space, data):
        self.met = False
        return True

class Bracket:
    def __init__(self, p, v1, v2, r, m=10):
        self.p = self.x, self.y = p
        self.v1 = v1
        self.v2 = v2
        self.r = r
        self.body = pymunk.Body(m)
        self.body.position = self.p

        self.s1 = pymunk.Segment(self.body, (0, 0), self.v1, self.r)
        self.s2 = pymunk.Segment(self.body, (0, 0), self.v2, self.r)
        self.s1.density = 1
        self.s2.density = 1
        SPACE.add(self.body, self.s1, self.s2)

        # super().__init__(*p)

class Seesaw:
    def __init__(self, center, beam_length: Vec2d, carrier_length):
        b0 = SPACE.static_body

        p = Vec2d(*center)
        v = Vec2d(*beam_length)
        v2 = Vec2d(*carrier_length)

        self.beam = Segment(p, v, category=1, mask=16)
        mid_local = 0.5 * v
        mid_world = p + mid_local  # Attach only at the middle
        PivotJoint(b0, self.beam.body, mid_world, mid_local, collide=False)

        # carriers
        self.carrier1 = Segment(p - v2 * 0.5, v2, m=100, damp=True, category=2, mask=20)
        PivotJoint(self.carrier1.body, self.beam.body, v2 * 0.5, (0, 0))

        self.carrier2 = Segment(p + v - v2 * 0.5, v2, m=100, damp=True, category=2, mask=20)
        PivotJoint(self.carrier2.body, self.beam.body, v2 * 0.5, v)

        fulcrum = Triangle(*mid_world, 50, pymunk.Body.STATIC, category=8, mask=1)


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

clickables = pygame.sprite.Group()
clicked = pygame.sprite.GroupSingle()

temp_joint = None
picking = False

won = pygame.event.custom_type()

class Level:
    def __init__(self, number: int, weights: list, level_type):
        self.number = number
        self.weight = weights

class App:
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.draw_options = DrawOptions(self.display)

        self.running = True

    def run(self):
        global temp_joint, picking
        while True:
            left_click = pygame.mouse.get_pressed()[0]
            # print('left_click', left_click)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == won:
                    print('YAY')
                    return

                # if event == pygame.MOUSEBUTTONUP:
                #     picking = False
                #     print('up')
                # if isinstance(temp_joint, PivotJoint):
                #     SPACE.remove(temp_joint.joint)

            for i in clickables:
                # todo make sprite group for clickables
                if left_click:
                    if i.rect.collidepoint(pygame.mouse.get_pos()):
                        picking = True
                        clicked.add(i)
                        # print("!!!!!")
                else:
                    picking = False
            if len(clicked) > 0:
                if picking:
                    clicked.sprite.body.body_type = pymunk.Body.KINEMATIC
                    clicked.sprite.body.position = pygame.mouse.get_pos()
                else:
                    clicked.sprite.body.body_type = pymunk.Body.DYNAMIC

            got_all = True
            for i in plat_list:
                if not i.met:
                    got_all = False
                    break
            if got_all:
                pygame.event.post(pygame.event.Event(won))
            print(got_all)

            bodies.update()
            joints.update()

            self.draw()

            self.clock.tick(60)
            SPACE.step(1 / 60)

    def draw(self):
        # images, blitting
        self.display.fill('gray')
        SPACE.debug_draw(DrawOptions(self.display))

        # global picking
        # i
        # for body in bodies:
        #     # print(body)
        #     body.draw(DISPLAY)
        # for joint in joints:
        #     # print(joint)
        #     joint.draw(DISPLAY)

        pygame.display.update()

        text = f'fpg: {self.clock.get_fps():.1f}'
        pygame.display.set_caption(text)


if __name__ == '__main__':

    Box((0, 0), (W / 2, H), category=16, mask=7)
    Box((W/2, 0), (W, H), category=16, mask=7)

    # todo make group for box #2
    # ball1 = Ball(100, 0, 5)
    level_weights = [10, 50, 40, 50]

    # baskets
    num = len(level_weights)
    l = W/2/num

    plat_list = []
    for i in range(num):
        plat = LoadingPlatform((W/2 + i *l, H - i * l), (l, 0),
                category=16, mask=7, collision_type=10+num+i)
        plat_list.append(plat)
        # when exactly one block is touching it,

    # block
    # i left like 10 collision types available
    blocks = pygame.sprite.Group()

    for i in range(num):
        b = Block(50 + i * 50, 50, m=level_weights[i], clickable=True,
                         category=4, mask=22, collision_type=10+i)
        blocks.add(b)

    handlers = [SPACE.add_collision_handler(10+num+i, 10+i) for i in range(num)]
    for i, handler in enumerate(handlers):
        handler.begin = plat_list[i].tagged
        handler.separate = plat_list[i].separated

    Seesaw((100, 350), (200, 0), (100, 0))


    # # Add all bodies and joints from the sprite groups to the space ONCE before the simulation loop
    for sprite in bodies:
        SPACE.add(sprite.body, sprite.shape)
    for sprite in joints:
        SPACE.add(sprite.joint)

    App().run()

    # print(SPACE.shapes)  # Should show a list of shapes
pygame.quit()
