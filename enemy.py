'''
Enemy classes for the game
Functions:
- Enemy: Base enemy class
- BasicEnemy: Simple enemy that moves towards player
- create_random_enemy: Factory function to create a random enemy type
'''

import pygame
import os
import random
from playerclasses import player

class Enemy(player):
    '''Base enemy class'''
    def __init__(self, cordx, cordy, maxhp, hp, score, speed=1, image_path='data/sprites/enemy.png', container=None):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(center=(cordx, cordy))
        self.pos = pygame.Vector2(cordx, cordy)
        self.health = hp
        self.max_health = maxhp
        self.speed = speed
        self.alive = True

    def update(self, player_pos):
        # Gets overridden in subclasses for different enemies
        pass
    
    def move_towards_player(self, player_x, player_y):
        # Basic movement towards player
        direction = pygame.Vector2(player_x, player_y) - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction
            self.rect.center = self.pos
    
    def drop_loot(self):
        # Placeholder for loot drop logic
        pass

class Salamander(Enemy):
    # Salamander - moves toward player
    def __init__(self, cordx, cordy, maxhp, hp, score, container = None):
        super().__init__(cordx, cordy, maxhp, hp, score, container)

    def update(self, player_pos):
        self.move_towards_player(player_pos)

class Eyeball(Enemy):
    # Eyeball - sits in one spot
    def __init__(self, cordx, cordy, maxhp, hp, score, container = None):
        super().__init__(cordx, cordy, maxhp, hp, score, container)

def create_random_enemy(cordx, cordy):
    # Make a random enemy at the given position
    enemy_types = [Salamander, Eyeball]
    enemy_class = random.choice(enemy_types)
    return enemy_class(cordx, cordy)