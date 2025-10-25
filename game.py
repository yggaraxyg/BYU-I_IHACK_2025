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
        self.player_pos = pygame.Vector2(60,60)
        self.player_image = pygame.image.load(os.path.join('data', 'sprites', 'player.png'))
        self.turtle_image = pygame.image.load(os.path.join('data', 'sprites', 'turtle.png'))
        self.player_sprite = pygame.sprite.GroupSingle()
        self.enemy_sprites = pygame.sprite.Group()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.get_input()
        self.player_update()
        self.sprite_update()
        self.dt = self.clock.tick(60)
        pass

    def on_render(self):
        self._screen.fill((0,0,0))
        self.player_sprite.draw(self._screen)
        self.enemy_sprites.draw(self._screen)
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
        self.player_pos = self.player_pos + self.velocity
        self.player = Player(self.player_pos, self.player_image)
        self.player_sprite.add(self.player)
    
    def enemy_sprites(self):
        self.turtlepos = pygame.Vector2(20, 20)
        self.turtle = Turtle(self.turtlepos, self.turtle_image)
        self.enemy_sprites.add(self.turtle)

    def sprite_update(self):
        pass

    def get_input(self):
        self.keys = pygame.key.get_pressed()
        self.speed = 1
        self.velocity = pygame.Vector2(0,0)
        if self.keys[pygame.K_LSHIFT]:
            self.speed = self.speed * 2
        if self.keys[pygame.K_w]:
            self.velocity.y -= self.speed * self.dt
        if self.keys[pygame.K_s]:
            self.velocity.y += self.speed * self.dt
        if self.keys[pygame.K_a]:
            self.velocity.x -= self.speed * self.dt
        if self.keys[pygame.K_d]:
            self.velocity.x += self.speed * self.dt
        





class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center = pos)

class Turtle(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center = pos)

if __name__ == "__main__" :
    world = World()
    world.on_execute()

pygame.quit
	
