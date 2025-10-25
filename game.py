import pygame
from pygame.locals import *
import os
import random
import pygame_menu
import pytmx
from pytmx.util_pygame import load_pygame
import tkinter
from tkinter import filedialog
from questionbackend import *

question_list = []
file_path = "data/questions/easy_mode.csv" # Default CSV file path

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
        self.map = pytmx.load_pygame(os.path.join('data', 'maps', 'map1.tmx'))
        self.map_pwidth = self.map.width * 16
        self.map_pheight = self.map.height * 16

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
        self.player.pos = self.player.pos + self.velocity
        self.player_sprite.update(self.player.pos - self.camera_pos)
        self.collision_check()

    
    def enemies_update(self):
        for enemy in self.enemy_sprites:
            enemy.move_towards(self.player.pos)

        
    def camera(self):
        self.camera_pos = self.player_pos - 0.5 * pygame.Vector2(self.width, self.height)
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

    def heal(self, num):
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
        
def start_game():
    world = World()
    world.on_execute()

def user_csv():
    # Load user csv file
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
    if file_path:
        print(f"Selected file: {file_path}")
        select_csv(file_path)
    else:
        print("No file selected.")
    
    root.destroy()    

def select_csv(file_path):
    global question_list
    question_list = []  # Clear existing questions
    question_box = questionbox()
    question_box.getFromCSV(file_path)
    
    question_list.extend(question_box.questionlist)
    print(f"Loaded {len(question_box.questionlist)} questions from {file_path}")
    print(f"Total questions in list: {len(question_list)}")

def create_questions_menu():
    theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    question_menu = pygame_menu.Menu('Manage ?s', 320, 240, theme=theme)

    csv_submenu = create_csv_menu()
    manual_submenu = create_manual_menu()

    question_menu.add.button("Manual Input", manual_submenu, font_size=15)
    question_menu.add.button("Choose Default CSV", csv_submenu, font_size=15)
    question_menu.add.button("Load User CSV", user_csv, font_size=15)
    question_menu.add.button("test csv", lambda: print(question_list), font_size=15)

    return question_menu

def create_csv_menu():
    theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    csv_menu = pygame_menu.Menu('Select CSV', 320, 240, theme=theme)

    csv_menu.add.button("Easy Mode", lambda: select_csv("data/questions/easy_mode.csv"), font_size=15)
    csv_menu.add.button("English", lambda: select_csv("data/questions/english.csv"), font_size=15)
    csv_menu.add.button("Geography", lambda: select_csv("data/questions/geography.csv"), font_size=15)
    '''csv_menu.add.button("Math", lambda: select_csv("data/questions/math.csv"), font_size=15)
    This one is broken because math.csv uses characters that break the parser'''
    csv_menu.add.button("Psych", lambda: select_csv("data/questions/psych.csv"), font_size=15)

    return csv_menu

def create_manual_menu():
    theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    manual_menu = pygame_menu.Menu('Manual Input', 320, 240, theme=theme)

    question_list = []  # Clear existing questions
    question_input = manual_menu.add.text_input("Question: ", default="", font_size=11)
    answer_input = manual_menu.add.text_input("Correct Answer: ", default="", font_size=11)
    
    def handle_manual_input():
        question_text = question_input.get_value()
        answer_text = answer_input.get_value()
        wrong1_text = wrong1_input.get_value()
        wrong2_text = wrong2_input.get_value()
        wrong3_text = wrong3_input.get_value()
        
        if question_text and answer_text and wrong1_text and wrong2_text and wrong3_text:
            question_box = questionbox()
            question_box.addQuestion(question_text, answer_text, wrong1_text, wrong2_text, wrong3_text)
            question_list.append(question_box.questionlist)
            print(f"Added question: {question_text} -> {answer_text} with wrong answers: {wrong1_text}, {wrong2_text}, {wrong3_text}")
            # Clear inputs
            question_input.set_value("")
            answer_input.set_value("")
            wrong1_input.set_value("")
            wrong2_input.set_value("")
            wrong3_input.set_value("")
        elif question_text and answer_text:
            question_box = questionbox()
            question_box.addQuestion(question_text, answer_text)
            question_list.append(question_box.questionlist)
            print(f"Added question: {question_text} -> {answer_text}")
            # Clear inputs
            question_input.set_value("")
            answer_input.set_value("")
            wrong1_input.set_value("")
            wrong2_input.set_value("")
            wrong3_input.set_value("")
        else:
            print("Please enter both question and answer")
    
    manual_menu.add.button("Add Question", handle_manual_input, font_size=12)
    manual_menu.add.label("Optional:", font_size=10)
    wrong1_input = manual_menu.add.text_input("Wrong Answer 1: ", default="", font_size=11)
    wrong2_input = manual_menu.add.text_input("Wrong Answer 2: ", default="", font_size=11)
    wrong3_input = manual_menu.add.text_input("Wrong Answer 3: ", default="", font_size=11)

    return manual_menu

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((320, 240), pygame.RESIZABLE | pygame.SCALED)
    
    custom_theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    menu = pygame_menu.Menu('', 320, 240, theme=custom_theme)
    
    questions_submenu = create_questions_menu()
    
    logo_image = os.path.join('data', 'sprites', 'logo.png')
    play_button_image = os.path.join('data', 'sprites', 'play_button.png')
    questions_button_image = os.path.join('data', 'sprites', 'questions_button.png')

    menu.add.image(logo_image)
    menu.add.vertical_margin(20)
    menu.add.banner(pygame_menu.BaseImage(image_path=play_button_image), start_game)
    menu.add.vertical_margin(10)
    menu.add.banner(pygame_menu.BaseImage(image_path=questions_button_image), questions_submenu)

    menu.mainloop(screen)
