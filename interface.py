from global_vars import *

import time


class ClickableSprite:  # mixin
    def __init__(self, single_click:bool=False):
        """Mixin class for adding the ability to be clicked and interacted by player mouse.
        Child needs to initialize ClickableSprite in its init class."""
        self.single_click = single_click
        clickables.add(self)
    def hover(self):
        pass
    def idle(self):
        pass
    def click(self):
        pass
    def drop(self):
        pass
    # def update(self):
    @abstractmethod
    def detect_hover(self) -> bool:
        return False
    def update(self):
        if clicked.has(self):
            self.click()
            if self.single_click:
                clicked.remove(self)
        else:
            if self.detect_hover():
                self.hover()
            else:
                self.idle()


class GameObject(pygame.sprite.DirtySprite):
    def __init__(self, x:int, y:int,
                 size:[int, int]=(0, 0), color=(255, 0, 0), *groups):
        super().__init__(non_physics_sprites, *groups)
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
        # self.game_sprite.rect.update(*get_rect(self.shape))
        self.draw()

    def rotate(self, angle_radians, x, y):
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(angle_radians))
        self.rect = self.image.get_rect(center=(x, y))

    def default_draw(self):
        pass
    def draw(self):
        """draws to image surface"""
        self.image.fill(self.color)
    def destroy(self):
        self.kill()  # because bodysprite has this method :(


class Text(pygame.sprite.DirtySprite):
    texts = pygame.sprite.Group()
    def __init__(self, string: str, x, y, size:int, font=None, color=(255, 0, 0),
                 time_limit=0, fade=50, fade_speed=0, **kwargs):
        # super().__init__(x=x, y=y, **kwargs)
        super().__init__(Text.texts)
        # self.add(Text.texts)

        self.string = string

        self.color = pygame.Color(color)
        self.font = pygame.font.SysFont(font, size)
        self.text = self.font.render(self.string, True, self.color)
        self.size = self.text.get_size()
        self.x, self.y, *_ = self.rect = pygame.Rect((x, y), self.size)

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
        # super().update()



    def draw(self, screen):
        self.image = clear_surface(*self.size)
        self.image.blit(self.text, self.text.get_rect())
        screen.blit(self.text, self.rect)
        # self.draw()



class Button(GameObject, ClickableSprite):
    buttons = pygame.sprite.Group()
    def __init__(self, x:int, y:int, text:str, color, event=None):


        self.x = int(x)
        self.y = int(y)
        self.string = text
        self.text = Text(text, x=x, y=y, size=40, color=color)
        super().__init__(x, y, self.text.text.get_size(), color=color)
        ClickableSprite.__init__(self, single_click=True)
        self.add(Button.buttons, clickables)
        self.event = event

    def detect_hover(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def hover(self):
        self.color = 'green'
    def idle(self):
        self.color = 'black'
    def click(self):
        self.color = 'red'
        pygame.event.post(pygame.event.Event(self.event))
    def update(self):
        ClickableSprite.update(self)
        self.text.update()
        self.size = self.text.text.get_size()
        GameObject.update(self)

        # self.rect.update(self.x, self.y, *self.text.text.get_size())
    def draw(self):
        pygame.draw.rect(self.image, self.color, self.text.text.get_rect(), 5)
        # self.text = Text(self.string, self.x, self.y, 40, self.color)

