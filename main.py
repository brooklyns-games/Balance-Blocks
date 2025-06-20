import random

import pygame
import pymunk
# print(pymunk.pygame_util)

from pymunk.pygame_util import DrawOptions

import time

from global_vars import *
from objects import *

pygame.font.init()

"""Started June 14 2025
from Pymunk Basics by Ear of Corn Programming
https://youtube.com/playlist?list=PL_N_kL9gRTm8lh7GxFHh3ym1RXi6I6c50&si=IqN679o1NsVTzN6q

"""




def clear_surface(w, h, fill=None):
    if fill is None:
        return pygame.Surface((w, h), pygame.SRCALPHA)
    else:
        s = pygame.Surface((w, h))
        s.fill(fill)
        return s

# def limit_velocity(body, gravity, damping, dt):
#     """
#     https://www.pymunk.org/en/latest/overview.html
#     :param body:
#     :param gravity
#     :param damping
#     :param dt
#     :return:
#     """
#     max_velocity = 1000
#     # pymunk.Body.update_velocity()

def flip(x, y, null=False, return_as=tuple):
    if not null:
        return return_as((x, H - y))
    else:
        return return_as((x, y))


def new_body_at(x=0, y=0, m=0, body_type=pymunk.Body.DYNAMIC, collision_type=0):
    b = pymunk.Body(m, body_type)
    b.position = flip(x, y)

    return b


class Text:
    def __init__(self, string, x, y, size, color=(0, 0, 0), font=None,):
        self.string = string
        self.color = color
        self.font = pygame.font.SysFont(font, size)
        self.text = self.font.render(self.string, True, self.color)

    def draw(self, s):
        s.blit(self.text, self.text.get_rect())

buttons = pygame.sprite.Group()
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color):
        super().__init__(buttons, clickables)
        self.x = int(x)
        self.y = int(y)
        self.string = text
        self.text = Text(text, x, y, 40, color)
        self.image = clear_surface(*self.text.text.get_size())
        self.rect = self.text.text.get_rect()
        # print(self.rect)
        self.color = color

        self.hovering = False

    def update(self):
        # pass
        self.hovering = self.rect.collidepoint(*pygame.mouse.get_pos())
        if self.hovering:
            self.color = 'green'
        else:
            self.color = 'black'
        if clicked.has(self):
            self.color = 'red'

        self.rect.update(self.x, self.y, *self.text.text.get_size())
        # self.draw(self.display)
    def draw(self):
        pygame.draw.rect(self.image, self.color, self.text.text.get_rect(), 5)
        self.text = Text(self.string, self.x, self.y, 40, self.color)
        self.text.draw(self.image)



clicked = pygame.sprite.GroupSingle()

temp_joint = None
picking = False

won = pygame.event.custom_type()
new_level = pygame.event.custom_type()
check = pygame.event.custom_type()

level_types = ['sort', 'total', 'balance', 'find']

class Level:
    def __init__(self, number: int, weights: list, level_type='sort'):
        """Manages level information and controls when to add level objects"""
        self.number = number
        self.weights = weights

        self.plats = []
        self.blocks = []

    def run(self):
        # Add only the current level's objects to SPACE
        for sprite in bodies:
            SPACE.add(sprite.body, sprite.shape)
        for sprite in joints:
            SPACE.add(sprite.joint)

    @staticmethod
    def base():
        # todo do you really want to add this every time?
        # todo make group for regular level stuff--the box, floor, etc
        Box((0, 0), (W / 2, H), category=16, mask=7)
        Box((W / 2, 0), (W, H), category=16, mask=7)

        Seesaw((100, 350), (200, 0), (100, 0))

        # todo make group for box #2

    def setup(self):
        self.base()
        # baskets
        num = len(self.weights)
        l = W / 2 / num

        # Create loading platforms
        for i in range(num):
            plat = LoadingPlatform((W / 2 + i * l, H - i * l), (l, 0),
                                   category=16, mask=7, collision_type=10 + num + i)
            self.plats.append(plat)

        # Create blocks
        coords = list(set((10 + i * (W / 2 - 20) / num, 50) for i in range(num))) # somehow randomize?
        print(coords)
        for i in range(num):
            b = Block(*coords[i], m=self.weights[i], clickable=True,
                      category=4, mask=22, collision_type=10 + i)
            # random.choice
            self.blocks.append(b)

        handlers = [SPACE.add_collision_handler(10 + num + i, 10 + i) for i in range(num)]
        for i, handler in enumerate(handlers):
            handler.begin = self.plats[i].tagged
            handler.separate = self.plats[i].separated


class App:
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.draw_options = DrawOptions(self.display)

        self.running = True

        self.level_num = -1
        self.level = None


    @staticmethod
    def handle_clicking():
        global picking, button1
        left_click = pygame.mouse.get_pressed()[0]
        for i in clickables:
            if left_click:
                if i.rect.collidepoint(pygame.mouse.get_pos()):
                    picking = True
                    clicked.add(i)
                if button1.rect.collidepoint(*pygame.mouse.get_pos()):
                    picking = True
                    clicked.add(button1)


            else:
                picking = False


        if len(clicked) > 0 and clicked.sprite in clickables:
            if hasattr(clicked.sprite, 'body'):
                if picking:
                    clicked.sprite.body.body_type = pymunk.Body.KINEMATIC
                    clicked.sprite.body.position = pygame.mouse.get_pos()
                if not picking:
                    print('not picking')
                    clicked.sprite.body.body_type = pymunk.Body.DYNAMIC
        if not picking:
            clicked.empty()


    def check_won(self):
        got_all = True
        if not isinstance(self.level, Level):
            return
        for i in self.level.plats:
            if not i.met:
                got_all = False
                break
        if got_all:
            pygame.event.post(pygame.event.Event(won))
        # print(got_all)

    def handle_events(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.running = False

        if event.type == new_level:
            # time.sleep(1)
            self.level_num += 1
            if self.level_num > len(LEVELS):
                print("There aren't enough levels.")
            self.level = LEVELS[self.level_num]

            self.level.setup()
            self.level.run()

        if event.type == won:
            print('you won this level')
            clear(SPACE)
            pygame.event.post(pygame.event.Event(new_level))
        if event.type == check:
            print('click!')
            self.check_won()
        if event.type == pygame.MOUSEBUTTONUP:
            if clicked.sprite == button1:
                pygame.event.post(pygame.event.Event(check))



    def run(self):
        global temp_joint

        pygame.event.post(pygame.event.Event(new_level))

        while self.running:
            for event in pygame.event.get():
                self.handle_events(event)

            self.handle_clicking()
            print(clicked)

            """
            create new body centered at mouse position
            Set pivot joint there, attached to that body and the clickable block
            """
            # if isinstance(temp_joint, PivotJoint):
            #     SPACE.remove(temp_joint.joint)
            buttons.update()

            bodies.update()
            joints.update()

            self.draw()

            self.clock.tick(60)
            SPACE.step(1 / 60)

    def draw(self):
        # images, blitting
        self.display.fill('gray')
        SPACE.debug_draw(DrawOptions(self.display))

        # for body in bodies:
        #     # print(body)
        #     body.draw(DISPLAY)
        # for joint in joints:
        #     # print(joint)
        #     joint.draw(DISPLAY)
        level_display = Text('Level ' + str(self.level_num + 1), 0, 0, 40)
        level_display.draw(self.display)

        for button in buttons:
            button.draw()
        buttons.draw(self.display)


        pygame.display.update()

        text = f'fpg: {self.clock.get_fps():.1f}'
        pygame.display.set_caption(text)

def clear(space):
    # todo find better way to clear objects in SPACE
    for shape in list(space.shapes):
        space.remove(shape)
    for body in list(space.bodies):
        space.remove(body)
    for constraint in list(space.constraints):
        space.remove(constraint)
    bodies.empty()
    joints.empty()


if __name__ == '__main__':
    # ball1 = Ball(100, 0, 5) # test ball
    level_weights = [
        [10, 10],  # todo allow same weight to mean same collision type
        [10, 50, 40, 50],
        [20, 20, 40]

    ]
    LEVELS = [Level(i, weights) for i, weights in enumerate(level_weights)]
    button1 = Button(W/2, 0, 'Check', (0, 0, 0))

    App().run()

    # print(SPACE.shapes)  # Should show a list of shapes
pygame.quit()
