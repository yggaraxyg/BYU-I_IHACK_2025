import pygame
from pygame.locals import *
import os
import random
'''import pygame_menu
import pytmx
from pytmx.util_pygame import load_pygame'''

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
        self.ogre_image = pygame.image.load(os.path.join('data', 'sprites', 'ogre.png'))
        self.eyeball_image = pygame.image.load(os.path.join('data', 'sprites', 'florb.png'))        
        self.player_sprite = pygame.sprite.GroupSingle()
        self.enemy_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.player = Player(pygame.Vector2(60,60))
        self.turtle = Turtle(pygame.Vector2(20, 20))
        self.salamander = Salamander(pygame.Vector2(100,100))
        self.player_sprite.add(self.player)
        self.enemy_sprites.add(self.turtle)
        self.enemy_sprites.add(self.salamander)
        self.last_hit_time = 0

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.get_input()
        self.player_update()
        self.enemies_update()
        self.sprite_update()

        self.kill()
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
        self.player.pos = self.player.pos + self.player.velocity
        self.player_sprite.update(self.player.pos)
        self.collision_check()

    
    def enemies_update(self):
        for enemy in self.enemy_sprites:
            enemy.move_towards(self.player.pos)


    def sprite_update(self):
        pass

    def collision_check(self):
        sprite_collision = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
        cooldown_time = 120
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time >= cooldown_time:
            if sprite_collision:
                self.last_hit_time = current_time
                self.player.hurt(1)
                self.player.pos -= self.player.facing * 2
        else:
            self.player.pos -= self.player.facing * 2
        sprite_collision = pygame.sprite.spritecollide(self.player, self.collectable_sprites, False)
        
    
    def kill(self):
        if self.player.hp <= 0:
            self.player.kill()

    def get_input(self):
        self.keys = pygame.key.get_pressed()
        self.player.velocity = pygame.Vector2(0,0)
        prev_facing = self.player.facing
        self.player.facing = pygame.Vector2(0,0)
        if self.keys[pygame.K_LSHIFT]:
            self.speedmult=2
        else:
            self.speedmult=1
        if self.keys[pygame.K_w]:
            self.player.velocity.y -= self.player.speed * self.dt * self.speedmult
            self.player.facing.y = -1
        if self.keys[pygame.K_s]:
            self.player.velocity.y += self.player.speed * self.dt * self.speedmult
            self.player.facing.y = 1
        if self.keys[pygame.K_a]:
            self.player.velocity.x -= self.player.speed * self.dt * self.speedmult
            self.player.facing.x = -1
        if self.keys[pygame.K_d]:
            self.player.velocity.x += self.player.speed * self.dt * self.speedmult
            self.player.facing.x = 1
        if self.player.facing == pygame.Vector2(0,0):
            self.player.facing = prev_facing




class GameEntity(pygame.sprite.Sprite):
    def __init__(self, pos, image, maxhp, hp, score, speed):
        super().__init__()
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(center = pos)
        self.maxhp= maxhp
        self.hp = hp
        self.score = score
        self.speed = speed
        self.velocity = 0
        self.facing = pygame.Vector2(0,0)

    def hpmod(self, num):
        self.hp+=num
        if (self.hp>=self.maxhp):
            self.hp=self.maxhp
        if (self.hp<=0):
            self.die()

    def heal(num):
        self.hpmod(num)

    def hurt(self,num):
        self.hpmod(-num)

    def scoremod(self, num):
        self.score+=num

    def score(self, num):
        self.scoremod(num)

    def penalize(self, num):
        self.scoremod(-num)

    def getscore(self):
        return self.score

    def gethp(self):
        return self.hp

    def getx(self):
        return self.cords[0]

    def gety(self):
        return self.cords[1]

    def setx(self, x):
        self.cords[0]=x

    def sety(self, y):
        self.cords[1]=y

    def die(self):
        self.kill

    def move_towards(self, pos):
        direction = pos-self.pos
        if(direction.length()>0):
            direction=direction.normalize()
            self.pos+=direction*self.speed
            self.rect.center=self.pos


class Player(GameEntity):
    def __init__(self, pos):
        super().__init__(pos, pygame.image.load(os.path.join('data', 'sprites', 'player.png')), 10, 10, 0, 0.1)
    
    def update(self, pos):
        self.rect = self.image.get_rect(center = pos)

class Turtle(GameEntity):
    def __init__(self, pos):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'turtle.png')), 25, 25, 10, 0)

class Treasure(GameEntity):
    def __init__(self, pos, score):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'coin.png')), 1, 1, score, 0)

class Heart(GameEntity):
    def __init__(self, pos, hp):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'heart.png')), hp, hp, 0 ,0)

class Salamander(GameEntity):
    def __init__(self, pos):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'salamander.png')), 20, 20, 40 , 0.25)
        
        
if __name__ == "__main__" :
    world = World()
    world.on_execute()

pygame.quit
	
