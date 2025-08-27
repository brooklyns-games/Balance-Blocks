from global_vars import *

import time

class GameObject(pygame.sprite.DirtySprite):
    def __init__(self, x:int, y:int,
                 size:[int, int]=(0, 0), color=(255, 0, 0), *groups):
        super().__init__(non_physics_sprites, *groups)
        # todo this has physics sprite as an attribute
        # self.physics_sprite = None

        self.x, self.y = x, y

        self.size = size
        self.color = pygame.Color(color)
        self.image = clear_surface(*self.size)
        self.image.fill(self.color)
        self.base_image = self.image.copy()

        self.rect = pygame.Rect(x, y, *self.size)

        self.dirty = 1
        # self.update()
    def update(self):
        """Updates rect, draws to image surface"""

        self.rect.update(self.x, self.y, *self.size)
        self.draw()

    def draw(self):
        """draws to image surface"""
        self.image.fill(self.color)

class LoadingBox(GameObject):
    loading_boxes = pygame.sprite.Group()
    def __init__(self, p0, size, **kwargs):

        """
        Makes an empty box with four walls, used to keep objects inside window
        *Does not add to bodies sprite group
        :param p0: top left corner
        :param size: bottom right corner
        :param d: radius of walls
        """
        x0, y0 = p0
        # x1, y1 = x0 + size[0], y0 + size[1]
        super().__init__(x=x0, y=y0, size=size, **kwargs)
        self.add(LoadingBox.loading_boxes)
        # self.vs = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            #

            # seg.color = color
            # SPACE.add(seg)
    def draw(self):
        super().draw()
        # print(self.rect)
        pygame.draw.rect(self.image, 'red', self.rect.inflate(-20, -20), 5)
        # for i in range(4):
            # pygame.draw.line(self.image, 'black', self.vs[i], self.vs[(i + 1) % 4], width=15)


class Text(GameObject):
    texts = pygame.sprite.Group()
    def __init__(self, string: str, x, y, size:int, font=None,
                 time_limit=0, fade=50, fade_speed=0, **kwargs):
        super().__init__(x=x, y=y, **kwargs)
        self.add(Text.texts)


        self.string = string

        self.font = pygame.font.SysFont(font, size)
        self.text = self.font.render(self.string, True, self.color)
        self.size = self.text.get_size()



        self.time_limit = time_limit
        self.t1 = time.time()
        self.t2 = None
        # self.t3 = None

        self.fade = fade
        self.fading = False

    def set_string(self, string):
        if string != self.string:
            self.string = string
            self.dirty = 1
            self.reset()

    def reset(self):
        self.text = self.font.render(self.string, True, self.color)
        self.size = self.text.get_size()
        self.rect = pygame.Rect(self.x, self.y, *self.size)

    def update(self):
        self.t2 = time.time()
        # print(self.t2)
        if self.time_limit > 0:
            # print('time limit')

            if not self.fading:
                # self.t2 = time.time()
                # print(self.t2 >= self.t1 + self.time_limit)
                if self.t2 >= self.t1 + self.time_limit:
                    self.fading = True

            else:  # first stage
                self.dirty = 1
                if self.color.a + self.fade >= 255:
                    self.kill()
                else:
                    # print(self.color.a)
                    self.color.a += self.fade
                    self.reset()
        super().update()



    def draw(self):
        self.image = clear_surface(*self.size)
        self.image.blit(self.text, self.text.get_rect())
        # self.draw()



class Button(GameObject):
    buttons = pygame.sprite.Group()
    def __init__(self, x:int, y:int, text:str, color):


        self.x = int(x)
        self.y = int(y)
        self.string = text
        self.text = Text(text, x=x, y=y, size=40, color=color)
        super().__init__(x, y, self.text.text.get_size(), color=color)
        self.add(Button.buttons, clickables)

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
        self.text.update()

        self.size = self.text.text.get_size()
        super().update()

        # self.rect.update(self.x, self.y, *self.text.text.get_size())
    def draw(self):
        pygame.draw.rect(self.image, self.color, self.text.text.get_rect(), 5)
        # self.text = Text(self.string, self.x, self.y, 40, self.color)

