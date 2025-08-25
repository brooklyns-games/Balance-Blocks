import random

import pygame
import pymunk
# print(pymunk.pygame_util)

from pymunk.pygame_util import DrawOptions

import time
import global_vars
from global_vars import clear_surface
from objects import *
from interface import *

pygame.font.init()

"""Started June 14 2025
from Pymunk Basics by Ear of Corn Programming
https://youtube.com/playlist?list=PL_N_kL9gRTm8lh7GxFHh3ym1RXi6I6c50&si=IqN679o1NsVTzN6q

"""


collision_types = {}



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
    """Pymunk's y coords start at bottom and not top of window"""
    if not null:
        return return_as((x, H - y))
    else:
        return return_as((x, y))


def new_body_at(x=0, y=0, m=0, body_type=pymunk.Body.DYNAMIC, collision_type=0):
    b = pymunk.Body(m, body_type)
    b.position = flip(x, y)

    return b






temp_joint = None
picking = False
check_button = Button(W / 2, 0, 'Check', (0, 255, 0))

# EVENTS = {}
won = pygame.event.custom_type()
new_level = pygame.event.custom_type()
check = pygame.event.custom_type()
wrong = pygame.event.custom_type()
start = pygame.event.custom_type()




class App:
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.draw_options = DrawOptions(self.display)

        self.basics = pygame.sprite.Group()

        self.running = True

        # self.level_num = -1
        self.level = None


        self.basics = pygame.sprite.Group()

        self.level_display = Text('yeet', 0, 0, 40)




    @staticmethod
    def handle_clicking():
        global picking, check_button
        left_click = pygame.mouse.get_pressed()[0]
        for i in clickables:
            if left_click:
                if i.rect.collidepoint(pygame.mouse.get_pos()):
                    picking = True
                    clicked.add(i)
                if check_button and check_button.rect.collidepoint(*pygame.mouse.get_pos()):
                    picking = True
                    clicked.add(check_button)


            else:
                picking = False


        if len(clicked) > 0 and clicked.sprite in clickables:
            if hasattr(clicked.sprite, 'body'):
                if picking:
                    clicked.sprite.body.body_type = pymunk.Body.KINEMATIC
                    clicked.sprite.body.position = pygame.mouse.get_pos()
                if not picking:
                    # print('not picking')
                    clicked.sprite.body.body_type = pymunk.Body.DYNAMIC
        if not picking:
            clicked.empty()


    def check_won(self):
        got_all = True
        if not isinstance(self.level, Level):
            return
        print(self.level.loading_platforms)
        for i in self.level.loading_platforms:
            print(i.met)
            if not i.met:
                got_all = False
                break
        if got_all:
            pygame.event.post(pygame.event.Event(won))
        else:
            pygame.event.post(pygame.event.Event(wrong))
        # print(got_all)

    def handle_events(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == start:
            global_vars.level_num = -1
            pygame.event.post(pygame.event.Event(new_level))
        if event.type == new_level:
            # print('new level!')
            # time.sleep(1)
            if self.level:  # get rid of last level
                self.level.end()
            global_vars.level_num += 1
            if global_vars.level_num > len(LEVELS):
                print("There aren't enough levels.")
            self.level = LEVELS[global_vars.level_num]
            self.level_display.set_string('Level ' + str(global_vars.level_num + 1))
            global_vars.LEVEL = self.level

            self.level.setup()
            self.level.run()

        if event.type == won:
            print('you won this level')
            clear()
            pygame.event.post(pygame.event.Event(new_level))
        if event.type == check:
            print('click!')
            self.check_won()
            self.level.guesses += 1


        if event.type == wrong:
            Text("Wrong!", 50, 200, 40, time_limit=1, fade=100).draw(self.display)
            self.level.wrongs += 1
            print('wrong! {}/{}'.format(self.level.wrongs, self.level.wrong_limit))
            if self.level.wrongs >= self.level.wrong_limit:
                print('you failed!')
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        if event.type == pygame.MOUSEBUTTONUP:
            if clicked.sprite == check_button:
                pygame.event.post(pygame.event.Event(check))

    # @staticmethod
    def base(self):
        # todo do you really want to add this every time?
        # todo make group for regular level stuff--the box, floor, etc

        Box((0, 0), (W / 2, H), category=16, mask=7)
        Box((W / 2, 0), (W, H), category=16, mask=7)

        Seesaw((100, 350), (200, 0), (100, 0))

        # todo make group for box #2

    def run(self):
        global temp_joint

        pygame.event.post(pygame.event.Event(new_level))
        self.base()

        while self.running:
            for event in pygame.event.get():
                self.handle_events(event)

            self.handle_clicking()

            # self.level.sprite_objects.update()
            Button.buttons.update()
            Text.texts.update()
            print(list(i.met for i in self.level.loading_platforms))
            # print(Text.texts)

            bodies.update()
            # joints.update()

            self.draw()

            self.clock.tick(60)
            SPACE.step(1 / 60)

    def draw(self):
        # images, blitting
        self.display.fill('gray')
        SPACE.debug_draw(DrawOptions(self.display))



        for button in Button.buttons:
            button.draw()
        Button.buttons.draw(self.display)
        Text.texts.draw(self.display)
        # for text in Text.texts:
        #     text.draw()
        self.level_display.draw(self.display)


        pygame.display.update()

        text = f'fpg: {self.clock.get_fps():.1f}'
        pygame.display.set_caption(text)





if __name__ == '__main__':
    # ball1 = Ball(100, 0, 5) # test ball


    LEVELS = [Level(i, weights) for i, weights in enumerate(global_vars.level_weights)]
    App().run()

    # print(SPACE.shapes)  # Should show a list of shapes
pygame.quit()
