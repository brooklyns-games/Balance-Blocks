from global_vars import *
from objects import *
import random
import time


class Text(pygame.sprite.DirtySprite):
    texts = pygame.sprite.Group()
    def __init__(self, string: str, x:int, y:int,
                 size:int, color=(255, 0, 0), font=None,
                 time_limit=0, fade=0, fade_speed=0):
        super().__init__(Text.texts)
        self.string = string
        self.color = pygame.Color(color)
        self.font = pygame.font.SysFont(font, size)
        self.text = self.font.render(self.string, True, self.color)

        self.time_limit = time_limit
        self.t1 = time.time()
        self.t2 = None
        self.t3 = None

        self.fade = fade
        self.fading = False

        self.x, self.y = x, y


        self.size = self.text.get_size()
        self.image = clear_surface(*self.size)
        self.rect = pygame.Rect(x, y, *self.size)
        self.update()

        # print(self.groups(), 'text groups')

    def set_string(self, string):
        if string != self.string:
            self.string = string
            self.dirty = 1
            self.text = self.font.render(self.string, True, self.color)
            self.size = self.text.get_size()
            self.rect = pygame.Rect(self.x, self.y, *self.size)

    def update(self):
        if self.time_limit > 0:


            if not self.fading:
                self.t2 = time.time()
                # print(self.t2 >= self.t1 + self.time_limit)
                if self.t2 >= self.t1 + self.time_limit:
                    self.fading = True

            else:  # first stage
                if self.color.r + self.fade >= 255:
                    self.kill()
                else:
                    self.color.r += self.fade



        self.image = clear_surface(*self.size)
        self.image.blit(self.text, self.text.get_rect())
        # self.draw()


    def draw(self, screen):

        screen.blit(self.image, self.rect)



level_types = ['sort', 'total', 'balance', 'find']

class Level:
    def __init__(self, number: int, weights: list, level_type='sort'):
        """Manages level information and controls when to add level objects"""
        self.number = number
        self.weights = weights
        self.level_type = level_type

        self.loading_platforms = []
        self.blocks = []
        self.seesaw = None  # should be sprite groupsingle()

        self.guesses = 0
        self.wrongs = 0
        self.wrong_limit = 3


        # self.sprite_objects = pygame.sprite.Group()
        # self.sprite_objects.add(self.level_display)
        self.bodies = []


    def run(self):
        # Add only the current level's objects to SPACE
        for sprite in bodies:
            SPACE.add(sprite.body, sprite.shape)
        # for sprite in joints:
        #     SPACE.add(sprite.joint)
    def end(self):
        for sprite in self.blocks + self.loading_platforms:
            SPACE.remove(sprite.body, sprite.shape)
        # for sprite in self.sprite_objects:
        #     sprite.kill()
        # self.sprite_objects.empty()

        global_vars.blocks.empty()



    def setup(self):
        # self.base()
        # baskets
        total_blocks = len(self.weights)
        l = W / 2 / total_blocks

        # Create loading platforms
        # for i in range(total_blocks):

        # Create blocks
        global_vars.blocks.empty()
        coords = [(10 + i * (W / 2 - 20) / total_blocks, 50) for i in range(total_blocks)] # somehow randomize?
        random.shuffle(coords)

        unique_weights = list(set(self.weights))
        weight_to_collision = {w: 10 + i for i, w in enumerate(unique_weights)}

        handlers = []
        for i in range(total_blocks):
            weight = self.weights[i]
            block_handler = weight_to_collision[weight]
            platform_handler = weight_to_collision[weight]  #  + len(unique_weights)
            print(block_handler, platform_handler)

            b = Block(*coords[i], m=weight, clickable=True,
                      category=4, mask=22, collision_type=block_handler)


            plat = LoadingPlatform((W / 2 + i * l, H - i * l), (l, 0),
                                   category=16, mask=7,
                                   collision_type=platform_handler,)
            self.loading_platforms.append(plat)
            global_vars.blocks.add(b)
            self.blocks.append(b)  # to keep everything in order

            handler = SPACE.add_collision_handler(block_handler, platform_handler)
            handler.begin = self.loading_platforms[i].tagged
            handler.separate = self.loading_platforms[i].separated
            handlers.append(handler)
        print(len(handlers))
        # self.sprite_objects.add(*self.loading_platforms, *self.blocks)
        # print(global_vars.blocks)

        # make handlers between each platform and block
        # matches up platform with corresponding block
        # todo equal weights should mean equal collision types
        # handlers = [SPACE.add_collision_handler(10 + len(unique_weights) + i, 10 + i) for i in range(total_blocks)]


        # handlers2 = []
        # for i in range(total_blocks):
        #     # print(j)
        #     handlers2 = [SPACE.add_collision_handler(10 + i, j)
        #              for j in range(len(Deck.decks))]
        #     for x, handler in enumerate(handlers2):
        #         handler.begin = self.blocks[i].touching
                # handler.separate = blocks[i].separated

        # print(list(global_vars.bodies))



class Button(pygame.sprite.Sprite):
    buttons = pygame.sprite.Group()
    def __init__(self, x:int, y:int, text:str, color):
        super().__init__(Button.buttons, clickables)
        self.x = int(x)
        self.y = int(y)
        self.string = text
        self.text = Text(text, x, y, 40, color)
        self.size = self.text.text.get_size()
        self.image = clear_surface(*self.size)
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
        # self.text.update()

        self.rect.update(self.x, self.y, *self.text.text.get_size())
        # self.draw(self.display)
    def draw(self):
        pygame.draw.rect(self.image, self.color, self.text.text.get_rect(), 5)
        # self.text = Text(self.string, self.x, self.y, 40, self.color)
        self.text.update()
        # self.text.draw()
