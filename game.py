import pygame
from pygame.locals import *
import os
import random
import pygame_menu
import pytmx
from pytmx.util_pygame import load_pygame

class World:
    def __init__(self):
        self._running = True
        self._screen = None
        self.size = self.width, self.height = 320, 240

    def on_init(self):
        pygame.init()
        self._flags = pygame.RESIZABLE | pygame.SCALED
        self._screen = pygame.display.set_mode(self.size, self._flags)
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.setup()

    def setup(self):
        self.camera_pos = pygame.Vector2(0,0)
        self.player_pos = pygame.Vector2(0,0)
        self.player_sprite = pygame.image.load(os.path.join('data', 'sprites', 'player.png'))

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.player_update()
        self.sprite_update()
        pass

    def on_render(self):
        self._screen.fill((0,0,0))
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def player_update(self):
        self.player = Player(self.player_pos, self.player_sprite)

    def sprite_update(self):



class Player:
    def __init__(self, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(center = pos)

if __name__ == "__main__" :
    world = World()
    world.on_execute()

pygame.quit
	
