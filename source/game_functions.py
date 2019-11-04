import os
import pygame
from abc import abstractmethod

keybinding = {
    'action': pygame.K_s,
    'jump': pygame.K_SPACE,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'down': pygame.K_DOWN
}


class State:
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.next = None
        self.persist = {}
    
    @abstractmethod
    def startup(self, current_time, persist):
        """abstract method"""

    def cleanup(self):
        self.done = False
        return self.persist
    
    @abstractmethod
    def update(sefl, surface, keys, current_time):
        """abstract method"""


class Control:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.done = False
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.current_time = 0.0
        self.keys = pygame.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None
    
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
    
    def update(self):
        self.current_time = pygame.time.get_ticks()
        if self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys, self.current_time)
    
    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                self.keys = pygame.key.get_pressed()
            elif event.type == pygame.KEYUP:
                self.keys = pygame.key.get_pressed()
    
    def main(self):
        while not self.done:
            self.event_loop()
            self.update()
            pygame.display.update()
            self.clock.tick(self.fps)


def get_image(sheet, x, y, width, height, colorkey, scale):
    image = pygame.Surface([width, height])
    rect = image.get_rect()

    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    image = pygame.transform.scale(image, (int(rect.width*scale), int(rect.height*scale)))

    return image


def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', '.jpygame', '.bmp', '.gif')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pygame.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics
