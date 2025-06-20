import pymunk
import pygame

W, H = 800, 400
SPACE = pymunk.Space()
SPACE.gravity = (0, 1000)

bodies = pygame.sprite.Group()
# joints = pygame.sprite.Group()