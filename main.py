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



def new_body_at(x=0, y=0, m=0, body_type=pymunk.Body.DYNAMIC, collision_type=0):
    b = pymunk.Body(m, body_type)
    b.position = flip(x, y)

    return b



temp_joint = None
picking = False
check_button = Button(W / 2,
                      0, 'Check', (0, 255, 0))

# EVENTS = {}
won = pygame.event.custom_type()
new_level = pygame.event.custom_type()
check = pygame.event.custom_type()
wrong = pygame.event.custom_type()
restart_level = pygame.event.custom_type()


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

        self.level_display = Text('yeet', x=0, y=0, size=40)




    @staticmethod
    def handle_clicking(event):
        global picking, check_button
        # print('\tclicked', clicked)
        # print(clickables.sprites())

        if event.type == pygame.MOUSEBUTTONDOWN:
            # print('click')
            for i in clickables:
                # "if hovering"

                if i.detect_hover():
                    clicked.add(i)
        if event.type == pygame.MOUSEBUTTONUP:
            if len(clicked) > 0:
                clicked.sprite.drop()
                clicked.empty()



    def check_won(self):
        got_all = True
        if not isinstance(self.level, Level):
            return

        for i in self.level.loading_platforms:
            # print(i.met)
            if not i.has_block:
                Text("Not all decks are filled!", 50, 200, 40, time_limit=1, fade=10)
                return
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
            return
        if event.type == restart_level:
            self.level_display.set_string('Level ' + str(global_vars.level_num + 1))
            self.level.setup()
            # self.level.run()
        if event.type == new_level:
            if self.level:  # get rid of last level
                self.level.end()
            global_vars.level_num += 1
            if global_vars.level_num > len(LEVELS):
                print("There aren't enough levels.")

            self.level = LEVELS[global_vars.level_num]
            pygame.event.post(pygame.event.Event(restart_level))

        if event.type == won:
            print('you won this level')
            # clear()
            pygame.event.post(pygame.event.Event(new_level))
        if event.type == check:
            print('click!')
            self.check_won()
            self.level.guesses += 1
        if event.type == wrong:
            Text("Wrong!", 50, 200, 40, time_limit=1, fade=10)
            self.level.wrongs += 1
            print('wrong! {}/{}'.format(self.level.wrongs, self.level.wrong_limit))
            if self.level.wrongs >= self.level.wrong_limit:
                print('you failed!')
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        if event.type == pygame.MOUSEBUTTONUP:
            if clicked.sprite == check_button:
                pygame.event.post(pygame.event.Event(check))

    @staticmethod
    def base():

        b = Box((0, 0), (W, H), category=16, mask=7)
        # self.basics.add(b)
        # Box((W / 2, 0), (W, H), category=16, mask=7)

        Seesaw((100, 350), (200, 0), (100, 0), )
        # print('base done')

        # todo make group for box #2

    def run(self):
        global temp_joint
        pygame.event.post(pygame.event.Event(new_level))
        self.base()
        while self.running:
            for event in pygame.event.get():
                self.handle_events(event)
                self.handle_clicking(event)



            # print(list(i.has_block for i in self.level.loading_platforms))

            # self.level.sprite_objects.update()
            SPACE.step(1 / FPS)

            for clickable in clickables:
                ClickableSprite.update(clickable)
            Button.buttons.update()
            Text.texts.update()
            non_physics_sprites.update()
            physics_sprites.update()
            BODIES.update()
            self.draw()
            pygame.display.update()



            text = f'fpg: {self.clock.get_fps():.1f}'
            pygame.display.set_caption(text)

            self.clock.tick(FPS)


    def draw(self):
        self.display.fill('gray')


        # for button in Button.buttons:
        #     button.draw()
        SPACE.debug_draw(DrawOptions(self.display))
        Button.buttons.draw(self.display)
        Text.texts.draw(self.display)
        non_physics_sprites.draw(self.display)
        physics_sprites.draw(self.display)
        # BODIES.draw(self.display)


        # self.level_display.draw(self.display)

if __name__ == '__main__':
    # ball1 = Ball(100, 0, 5) # test ball
    LEVELS = [Level(i, weights) for i, weights in enumerate(global_vars.level_weights)]
    App().run()

    # print(SPACE.shapes)  # Should show a list of shapes
pygame.quit()
