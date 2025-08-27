import pymunk
import pygame


FPS = 60  # frames per second
W, H = 800, 400
SPACE = pymunk.Space()
SPACE.gravity = (0, 1000)

b0 = SPACE.static_body
BODIES = pygame.sprite.Group()
# joints = pygame.sprite.Group()
BLOCKS = pygame.sprite.Group()
clickables = pygame.sprite.Group() # sprites that can be interacted with by mouse
non_physics_sprites = pygame.sprite.Group()



level_weights = [
        [10, 10],  # todo allow same weight to mean same collision type
        [10, 30, 60],
        [10, 50, 40, 50],
        [20, 20, 40]

    ]


level_num = -1  # default is -1
# LEVEL = None

def clear_surface(w, h, fill=None):
    if fill is None:
        return pygame.Surface((w, h), pygame.SRCALPHA)
    else:
        s = pygame.Surface((w, h))
        s.fill(fill)
        return s


def clear():
    # todo find better way to clear objects in SPACE
    global SPACE
    SPACE = pymunk.Space()

    BODIES.empty()
    # joints.empty()

def float_to_int(floats):
    return tuple(int(f) for f in floats)

clicked = pygame.sprite.GroupSingle()