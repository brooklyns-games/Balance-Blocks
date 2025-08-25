import pymunk
import pygame

W, H = 800, 400
SPACE = pymunk.Space()
SPACE.gravity = (0, 1000)

bodies = pygame.sprite.Group()
# joints = pygame.sprite.Group()
blocks = pygame.sprite.Group()

level_weights = [
        [10, 10],  # todo allow same weight to mean same collision type
        [10, 30, 60],
        [10, 50, 40, 50],
        [20, 20, 40]

    ]


level_num = -1  # default is -1
LEVEL = None

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
    # for shape in list(space.shapes):
    #     space.remove(shape)
    # for body in list(space.bodies):
    #     space.remove(body)
    # for constraint in list(space.constraints):
    #     space.remove(constraint)

    bodies.empty()
    # joints.empty()

clicked = pygame.sprite.GroupSingle()