import os
import pygame
from source import constants as c
from source import game_functions

pygame.init()
pygame.event.set_allowed([pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT])
pygame.display.set_caption(c.GAME_TITLE)
SCREEN = pygame.display.set_mode(c.SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()
GFX = game_functions.load_all_gfx(os.path.join("assets"))
