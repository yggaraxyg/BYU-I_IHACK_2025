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
        self.camera_pos = pygame.Vector2(-0.5 * self.width,-0.5 * self.height)
        self.player_pos = pygame.Vector2(60,60)
        self.player_image = pygame.image.load(os.path.join('data', 'sprites', 'player.png'))
        self.turtle_image = pygame.image.load(os.path.join('data', 'sprites', 'turtle.png'))
        self.player_sprite = pygame.sprite.GroupSingle()
        self.enemy_sprites = pygame.sprite.Group()
        self.player_health = 10
        self.player = Player(self.player_pos, self.player_image)
        self.turtle_pos = pygame.Vector2(20, 20)
        self.turtle = Turtle(self.turtle_pos, self.turtle_image)
        self.enemy_sprites.add(self.turtle)
        self.player_sprite.add(self.player)
        self.last_hit_time = 0
        self.player_facing = pygame.Vector2(0,0)
        self.map = pytmx.load_pygame(os.path.join('data', 'maps', 'map1.tmx'))
        self.map_pwidth = self.map.width * 16
        self.map_pheight = self.map.width * 16

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.get_input()
        self.player_update()
        self.camera()
        self.enemies_update()
        self.sprite_update()
        
        self.kill()
        self.dt = self.clock.tick(60)
        pass

    def on_render(self):
        self._screen.fill((0,0,0))
        for row in range(self.map.width):
            for column in range (self.map.height):
                self.mapdisplay = pygame.Vector2(row * 16, column * 16) - self.camera_pos
                try:
                    tile = self.map.get_tile_image(row, column, 0)
                except:
                    pass
                if tile:
                    self._screen.blit(tile, self.mapdisplay)
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
        self.player_sprite.update(self.player_pos - self.camera_pos)
        self.collision_check()

    
    def enemies_update(self):
        pass

        
    def camera(self):
        self.camera_pos = self.camera_pos + self.velocity
        if self.camera_pos.x <= 0:
            self.camera_pos.x = 0
        if self.camera_pos.y <= 0:
            self.camera_pos.y = 0
        if self.camera_pos.x >= self.map_pwidth - self.width:
            self.camera_pos.x = self.map_pwidth - self.width
        if self.camera_pos.y >= self.map_pheight - self.height:
            self.camera_pos.y = self.map_pheight - self.height

    def sprite_update(self):
        pass

    def collision_check(self):
        sprite_collision = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
        cooldown_time = 120
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time >= cooldown_time:
            if sprite_collision:
                self.last_hit_time = current_time
                self.player_health -= 1
                self.player_pos -= self.player_facing * 2
        else:
            self.player_pos -= self.player_facing * 2
    
    def kill(self):
        if self.player_health <= 0:
            self.player.kill()

    def get_input(self):
        self.keys = pygame.key.get_pressed()
        self.speed = 0.1
        self.velocity = pygame.Vector2(0,0)
        prev_facing = self.player_facing
        self.player_facing = pygame.Vector2(0,0)
        if self.keys[pygame.K_LSHIFT]:
            self.speed = self.speed * 2
        if self.keys[pygame.K_w]:
            self.velocity.y -= self.speed * self.dt
            self.player_facing.y = -1
        if self.keys[pygame.K_s]:
            self.velocity.y += self.speed * self.dt
            self.player_facing.y = 1
        if self.keys[pygame.K_a]:
            self.velocity.x -= self.speed * self.dt
            self.player_facing.x = -1
        if self.keys[pygame.K_d]:
            self.velocity.x += self.speed * self.dt
            self.player_facing.x = 1
        if self.player_facing == pygame.Vector2(0,0):
            self.player_facing = prev_facing





class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center = pos)
    
    def update(self, pos):
        self.rect = self.image.get_rect(center = pos)

class Turtle(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center = pos)

def start_game():
    world = World()
    world.on_execute()

def show_questions():
    print("If only this did something")
    pass # Todo

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((320, 240), pygame.RESIZABLE | pygame.SCALED)
    
    custom_theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    menu = pygame_menu.Menu('', 320, 240, theme=custom_theme)
    
    logo_image = os.path.join('data', 'sprites', 'logo.png')
    play_button_image = os.path.join('data', 'sprites', 'play_button.png')
    questions_button_image = os.path.join('data', 'sprites', 'questions_button.png')

    menu.add.image(logo_image)
    menu.add.vertical_margin(20)
    menu.add.banner(pygame_menu.BaseImage(image_path=play_button_image), start_game)
    menu.add.vertical_margin(10)
    menu.add.banner(pygame_menu.BaseImage(image_path=questions_button_image), show_questions)

    menu.mainloop(screen)
