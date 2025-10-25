import pygame
from pygame.locals import *
import os
import sys
import random
import pygame_menu
import pytmx
from pytmx.util_pygame import load_pygame
import tkinter
from tkinter import filedialog
from questionbackend import *

question_list = []
file_path = "data/questions/easy_mode.csv" # Default CSV file path
wincondition = 0
winquantity = 10 
starttime =0

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
        global question_list
        global starttime

        if starttime == 0:
            starttime = pygame.time.get_ticks()

        if not question_list:
            try:
                question_box = questionbox()
                question_box.getFromCSV(file_path)
                question_list.extend(question_box.questionlist)
                print(f"Loaded {len(question_box.questionlist)} default questions")
            except Exception as e:
                print(f"Could not load default questions: {e}")
        
        self.camera_pos = pygame.Vector2(-0.5 * self.width,-0.5 * self.height)
        self.player_sprite = pygame.sprite.GroupSingle()
        self.enemy_sprites = pygame.sprite.Group()
        self.collectable_sprites = pygame.sprite.Group()
        self.player = Player(pygame.Vector2(60,60))
        self.turtle = Turtle(pygame.Vector2(20, 20))
        self.player_sprite.add(self.player)
        self.enemy_sprites.add(self.turtle)
        self.last_hit_time = 0
        self.map = pytmx.load_pygame(os.path.join('data', 'maps', 'map1.tmx'))
        self.map_pwidth = self.map.width * 16
        self.map_pheight = self.map.height * 16
        self.last_spawn = 0
        self.last_moved = 0 
        self.cameralock = pygame.Vector2(1,1)
        self.collisionmap()
        self.weapon_sprites = pygame.sprite.Group()
        self.attack_cooldown = 0
        self.correct=0
        self.answers=0;
        self.knockbackdir = pygame.Vector2(0,0)

    def on_loop(self):
        self.get_input()

        self.player_update()
        self.camera()
      
        self.enemies_update()

        self.sprite_update()
        
        self.weapon_update()
        self.kill()
        self.dt = self.clock.tick(60)

        if((pygame.time.get_ticks()-self.last_moved)>20000):
            delay = 200
        else:
            delay = 2000           
        if ((pygame.time.get_ticks()-self.last_spawn)>delay):
            self.last_spawn = pygame.time.get_ticks()
            self.spawn_random()
            
            
        pass

    def on_render(self):
        global wincondition
        global winquantity
        self._screen.fill((0,0,0))
        for row in range(self.map.width):
            for column in range (self.map.height):
                offsetx = 0
                offsety = 0
                self.mapdisplay = pygame.Vector2(row * 16 + offsetx, column * 16 + offsety) - self.camera_pos
                try:
                    tile = self.map.get_tile_image(row, column, 0)
                except:
                    pass
                if tile:
                    self._screen.blit(tile, self.mapdisplay)
        self.player_sprite.draw(self._screen)
        self.enemy_sprites.draw(self._screen)
        self.collectable_sprites.draw(self._screen)
        self.weapon_sprites.draw(self._screen)
        font = pygame.font.SysFont("Courier", 11)
        text_surface = font.render(f"Score:{self.player.score} HP:{self.player.hp} Time:{((pygame.time.get_ticks()-starttime)/1000):.2f}s Correct:{self.correct}/{self.answers}", True, (150, 150, 150))
        if ((wincondition==3) and (winquantity<=((pygame.time.get_ticks()-starttime)/1000))):
            self.game_over("YOU WIN!")
        self._screen.blit(text_surface, (10, 10))
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()
        sys.exit()

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
        self.player_relative = self.player.pos - self.camera_pos
        self.player.update_sprite(self.player.facing)
        self.player_sprite.update(self.player_relative)
        self.player.update_rect(self.camera_pos)
        self.collision_check()

    
    def enemies_update(self):
        for enemy in self.enemy_sprites:
            enemy.move_towards(self.player.pos)
            enemy.update_sprite(self.player.pos - enemy.pos)
            enemy.update_rect(self.camera_pos)

    def spawn_random(self):
        etypes = [Salamander, Salamander, Salamander, Salamander, Salamander, Eyeball, Eyeball, Eyeball, Eyeball, Eyeball, Ogre]
        self.spawn = random.choice(etypes)(pygame.Vector2(random.randint(0,768),random.randint(0,1152)))
        self.enemy_sprites.add(self.spawn)
            
        
    def camera(self):
        self.cameralock = pygame.Vector2(1,1)
        self.camera_next_pos = self.player.pos - 0.5 * pygame.Vector2(self.width, self.height)
        if self.camera_next_pos.x <= 0:
            self.camera_next_pos.x = 0
            self.cameralock.x = 0
        if self.camera_next_pos.y <= 0:
            self.camera_next_pos.y = 0
            self.cameralock.y = 0
        if self.camera_next_pos.x >= self.map_pwidth - self.width:
            self.camera_next_pos.x = self.map_pwidth - self.width
            self.cameralock.x = 0
        if self.camera_next_pos.y >= self.map_pheight - self.height:
            self.camera_next_pos.y = self.map_pheight - self.height
            self.cameralock.y = 0
        self.camera_move = self.camera_next_pos - self.camera_pos
        self.camera_pos = self.camera_next_pos

    def sprite_update(self):
        for sprite in self.collectable_sprites:
            sprite.cam(self.camera_pos)
        pass

    def collision_check(self):
        global wincondition
        global winquantity
        global starttime
        sprite_collision = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
        
        cooldown_time = 250
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time >= cooldown_time:
            if sprite_collision:
                for enemy in self.enemy_sprites:
                    if pygame.sprite.collide_rect(enemy, self.player):
                        
                        self.knockbackdir = self.player.pos - enemy.pos
                        #print (str(knockbackdir))
                        
                #print(type(sprite_collision[0]))
                self.last_hit_time = current_time
                if(type(sprite_collision[0])==Ogre):
                    self.player.hurt(2)
                self.player.hurt(1)
                try:
                    self.player.pos += (self.knockbackdir / 4)
                except Exception as e:
                    print (e)
        else:
            self.player.pos -= self.player.facing * 2
            self.player.pos += (self.knockbackdir / 8)


        for col in self.collectable_sprites:
            sprite_collision = pygame.sprite.spritecollide(col, self.player_sprite, False)
            if sprite_collision:
                self.answers+=1
                shortdelay = pygame.time.get_ticks()
                if(self.show_question_popup()):
                    self.correct+=1
                    if (abs(col.score)>abs(col.hp)):
                        self.player.score+=col.score
                    else:
                        self.player.hpmod(col.hp)
                        
                starttime+=(pygame.time.get_ticks()-shortdelay)
                col.die()
                
                if((wincondition==1) and (winquantity<=self.correct)):
                    self.game_over("YOU WIN!")
                if((wincondition==4) and (winquantity<=self.answers)):
                    self.game_over("YOU WIN!")
                if((wincondition==2) and (winquantity<=self.player.score)):
                    self.game_over("YOU WIN!")

        prev_tile =  pygame.Vector2(self.player.pos.x / 16, self.player.pos.y /16)    
        next_pos = self.player.pos + self.player.velocity
        next_tile =  pygame.Vector2(next_pos.x / 16 , next_pos.y /16)           
        tile = self.map.get_tile_gid(next_tile.x, next_tile.y, 1)
        self.tile_pos = pygame.Vector2(self.player.pos.x - (prev_tile.x * 16), self.player.pos.y - (prev_tile.y * 16))
        if tile:
            if self.player.velocity.x > 0 and next_tile.x != prev_tile.x and next_tile.y == prev_tile.y:
                self.player.pos.x = (int(next_tile.x) * 16) - 1
            if self.player.velocity.x < 0 and next_tile.x != prev_tile.x and next_tile.y == prev_tile.y:
                self.player.pos.x = (int(next_tile.x) * 16) + 16
            if self.player.velocity.y > 0 and next_tile.y != prev_tile.y and next_tile.x == prev_tile.x:
                self.player.pos.y = (int(next_tile.y) * 16) - 1
            if self.player.velocity.y < 0 and next_tile.y != prev_tile.y and next_tile.x == prev_tile.x:
                self.player.pos.y = (int(next_tile.y) * 16) + 16
            if self.map.get_tile_gid(next_tile.x, prev_tile.y, 1) == 0:
                self.player.pos.x = next_pos.x
            if self.map.get_tile_gid(prev_tile.x, next_tile.y, 1) == 0:
                self.player.pos.y = next_pos.y

        else:
            self.player.pos= next_pos


    def kill(self):
        if self.player.hp <= 0:
            self.player.kill()
            self._running = False
            self.game_over("GAME OVER")

    def game_over(self, message):
        print("Game Over")
        theme = pygame_menu.Theme(background_color=(50, 50, 50, 200),
                                 title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
        
        game_over_menu = pygame_menu.Menu('', 320, 240, theme=theme)
        game_over_menu.add.label(message, font_size=20, font_color=(255, 0, 0))
        game_over_menu.add.vertical_margin(10)
        game_over_menu.add.button("Restart", self.restart_game, font_size=15)
        game_over_menu.add.button("Main Menu", self.return_to_main_menu, font_size=15)
        game_over_menu.add.button("Quit", pygame_menu.events.EXIT, font_size=15)

        try:
            game_over_menu.mainloop(self._screen)
        except Exception as e:
            pass

    def restart_game(self):
        start_game()

    def return_to_main_menu(self):
        menu = main_menu()

        try:
            menu.mainloop(self._screen)
        except Exception as e:
            pass
        finally:
            pygame.quit()
            sys.exit()

    def get_input(self):
        global starttime
        self.keys = pygame.key.get_pressed()
        self.player.velocity = pygame.Vector2(0,0)
        prev_facing = self.player.facing
        self.player.facing = pygame.Vector2(0,0)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= self.dt
        
        if self.keys[pygame.K_LSHIFT]:
            self.speedmult=2
        else:
            self.speedmult=1
        if self.keys[pygame.K_w]:
            self.player.velocity.y -= self.player.speed * self.dt * self.speedmult
            self.player.facing.y = -1
            self.last_moved= pygame.time.get_ticks()
        if self.keys[pygame.K_s]:
            self.player.velocity.y += self.player.speed * self.dt * self.speedmult
            self.player.facing.y = 1
            self.last_moved= pygame.time.get_ticks()
        if self.keys[pygame.K_a]:
            self.player.velocity.x -= self.player.speed * self.dt * self.speedmult
            self.player.facing.x = -1
            self.last_moved= pygame.time.get_ticks()
        if self.keys[pygame.K_d]:
            self.player.velocity.x += self.player.speed * self.dt * self.speedmult
            self.player.facing.x = 1
            self.last_moved= pygame.time.get_ticks()

        if self.keys[pygame.K_ESCAPE]:
            shortdelay=pygame.time.get_ticks()
            pause = pause_menu()
            try:
                pause.mainloop(self._screen)
            except Exception as e:
                pass
            
            starttime+=(pygame.time.get_ticks()-shortdelay)

        if self.attack_cooldown <= 0:
            if self.keys[pygame.K_UP]:
                self.attack('up')
                self.attack_cooldown = 300
            elif self.keys[pygame.K_DOWN]:
                self.attack('down')
                self.attack_cooldown = 300
            elif self.keys[pygame.K_LEFT]:
                self.attack('left')
                self.attack_cooldown = 300
            elif self.keys[pygame.K_RIGHT]:
                self.attack('right')
                self.attack_cooldown = 300
        
        if self.player.facing == pygame.Vector2(0,0):
            self.player.facing = prev_facing

    def attack(self, direction):
        self.weapon_sprites.empty()
        
        sword_offset = 20
        match direction:
            case 'up':
                sword_pos = self.player.pos + pygame.Vector2(0, -sword_offset)
                rotation = 0
            case 'down':
                sword_pos = self.player.pos + pygame.Vector2(0, sword_offset)
                rotation = 180
            case 'left':
                sword_pos = self.player.pos + pygame.Vector2(-sword_offset, 0)
                rotation = 90
            case 'right':
                sword_pos = self.player.pos + pygame.Vector2(sword_offset, 0)
                rotation = 270
        
        sword = Weapon(sword_pos, rotation)
        self.weapon_sprites.add(sword)
        sword.update_rect(self.camera_pos)
        self.check_weapon_collision()

    def weapon_update(self):
        for weapon in self.weapon_sprites:
            weapon.update_rect(self.camera_pos)

    def check_weapon_collision(self):
        for weapon in self.weapon_sprites:
            hit_enemies = pygame.sprite.spritecollide(weapon, self.enemy_sprites, False)
            for enemy in hit_enemies:
                enemy.hurt(5)
                if enemy.hp <= 0:
                    if(random.choice([True,False])):
                        glob=Heart(enemy.pos, (enemy.score/5))
                    else:
                        glob=Treasure(enemy.pos, enemy.score)
                    self.collectable_sprites.add(glob)
                    enemy.die()
        
        pygame.time.set_timer(pygame.USEREVENT + 1, 150)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.USEREVENT + 1:
            self.weapon_sprites.empty()
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)

    def collisionmap(self):
            self.collision_tiles = []
            for layer in self.map.visible_layers:
                if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == "Collision Layer":
                    for obj in layer:
                        self.collision_tiles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
    
    def show_question_popup(self):
        global question_list
        
        if not question_list:
            print("No questions available.")
            return
        
        question_box = questionbox()
        question_box.questionlist = question_list
        question_set = question_box.getQuestion()

        self.current_question_set = question_set
        
        question_text = question_set[0]
        answer1 = question_set[1]
        answer2 = question_set[2]
        answer3 = question_set[3]
        answer4 = question_set[4]
        correct_answer_index = question_set[5]
        
        self.question_result = None

        question_theme = pygame_menu.Theme(
            background_color=(50, 50, 50, 200),
            title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE
        )

        self.question_menu = pygame_menu.Menu('', 280, 180, theme=question_theme)
        
        self.question_menu.add.label(question_text, max_char=30, font_size=11, font_color=(255, 255, 255), align=pygame_menu.locals.ALIGN_CENTER)
        self.question_menu.add.vertical_margin(10)
        self.question_menu.add.button(f"A) {answer1}", lambda: self.answer_question(0, correct_answer_index, self.question_menu), font_size=10)
        self.question_menu.add.button(f"B) {answer2}", lambda: self.answer_question(1, correct_answer_index, self.question_menu), font_size=10)
        self.question_menu.add.button(f"C) {answer3}", lambda: self.answer_question(2, correct_answer_index, self.question_menu), font_size=10)
        self.question_menu.add.button(f"D) {answer4}", lambda: self.answer_question(3, correct_answer_index, self.question_menu), font_size=10)
        
        self.question_menu.mainloop(self._screen)

        return self.question_result

    def answer_question(self, selected_answer, correct_answer, menu):
        question_set = self.current_question_set
        correct_answer_text = question_set[correct_answer + 1]
        if selected_answer == correct_answer:
            print("correct")
            self.question_feedback(True)
            self.question_result = True
        else:
            print("wrong")
            self.question_feedback(False, correct_answer_text)
            self.question_result = False
            
        exit_menu(menu)
    
    def question_feedback(self, correct, correct_answer=None):
        feedback_theme = pygame_menu.Theme(
            background_color=(50, 50, 50, 200),
            title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE
        )

        feedback_menu = pygame_menu.Menu('', 280, 180, theme=feedback_theme)
        
        if correct:
            feedback_menu.add.label("Correct!", font_size=18, font_color=(0, 255, 0), align=pygame_menu.locals.ALIGN_CENTER)
        else:
            feedback_menu.add.label(f"Incorrect. The answer was {correct_answer}.", font_size=13, font_color=(255, 0, 0), align=pygame_menu.locals.ALIGN_CENTER)
        
        feedback_menu.add.vertical_margin(10)
        feedback_menu.add.button("Continue", lambda: exit_menu(feedback_menu), font_size=15)
        
        feedback_menu.mainloop(self._screen)


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
        self.velocity = pygame.Vector2(0,0)
        self.facing = pygame.Vector2(0,0)
        self.cords = [pos.x, pos.y]

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
        self.kill()
        del(self)

    def move_towards(self, pos):
        direction = pos-self.pos
        if(direction.length()>0):
            direction=direction.normalize()
            self.pos+=direction*self.speed
            self.rect.center=self.pos
    
    def update_rect(self, camera_pos):
        self.rect.center = self.pos - camera_pos
        
    def cam(self, cam):
        self.rect = self.image.get_rect(center = self.pos - cam)


class Player(GameEntity):
    def __init__(self, pos):

        self.sprites = {
            'up': pygame.image.load(os.path.join('data', 'sprites', 'player_up.png')),
            'down': pygame.image.load(os.path.join('data', 'sprites', 'player.png')),
            'left': pygame.image.load(os.path.join('data', 'sprites', 'player_left.png')),
            'right': pygame.image.load(os.path.join('data', 'sprites', 'player_right.png')),
        }

        super().__init__(pos, self.sprites['down'], 10, 10, 0, 0.1)
        self.current_direction = 'down'
    
    def update_sprite(self, facing_direction):
        new_direction = 'down'
        if facing_direction.y < 0:
            new_direction = 'up'
        elif facing_direction.y > 0:
            new_direction = 'down'
        elif facing_direction.x < 0:
            new_direction = 'left'
        elif facing_direction.x > 0:
            new_direction = 'right'

        if new_direction != self.current_direction:
            self.current_direction = new_direction
            self.image = self.sprites[new_direction]
    
    def update(self, pos):
        self.rect = self.image.get_rect(center = pos)

class Weapon(GameEntity):
    def __init__(self, pos, rotation=0):
        sprite_image = pygame.image.load(os.path.join('data', 'sprites', 'sword.png'))
        rotated_image = pygame.transform.rotate(sprite_image, rotation)
        super().__init__(pos, rotated_image, 1, 1, 0, 0)
        self.rotation = rotation
    
    def update(self, camera_pos):
        self.rect.center = self.pos - camera_pos

class Turtle(GameEntity):
    def __init__(self, pos):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'turtle.png')), 25, 25, 10, 0)
    
    def update_sprite(self, facing_direction):
        self.image = pygame.image.load(os.path.join('data', 'sprites', 'turtle.png'))


class Treasure(GameEntity):
    def __init__(self, pos, score):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'coin.png')), 1, 1, score, 0)

class Heart(GameEntity):
    def __init__(self, pos, hp):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'heart.png')), hp, hp, 0 ,0)

class Salamander(GameEntity):
    def __init__(self, pos):
        self.sprites = {
            'right': pygame.image.load(os.path.join('data', 'sprites', 'salamander.png')),
            'left': pygame.transform.flip(pygame.image.load(os.path.join('data', 'sprites', 'salamander.png')), True, False),
        }

        super().__init__(pos,self.sprites['right'], 10, 10, 20 , 0.20)        

    def update_sprite(self, facing_direction):
        if facing_direction.x < 0:
            self.image = self.sprites['left']
        else:
            self.image = self.sprites['right']

class Eyeball(GameEntity):
    def __init__(self, pos):
        super().__init__(pos,pygame.image.load(os.path.join('data', 'sprites', 'florb.png')), 20, 20, 10 , 0)
    
    def update_sprite(self, facing_direction):
        self.image = pygame.image.load(os.path.join('data', 'sprites', 'florb.png'))

class Ogre(GameEntity):
    def __init__(self, pos):
        self.sprites = {
            'right': pygame.image.load(os.path.join('data', 'sprites', 'ogre.png')),
            'left': pygame.transform.flip(pygame.image.load(os.path.join('data', 'sprites', 'ogre.png')), True, False),
        }
        
        super().__init__(pos,self.sprites['right'], 100, 100, 100 , 0.05)
        self.current_direction = 'right'
    
    def update_sprite(self, facing_direction):
        if facing_direction.x < 0:
            self.image = self.sprites['left']
        else:
            self.image = self.sprites['right']
def start_game():
    global starttime
    starttime = (pygame.time.get_ticks())
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
    
    question_menu = pygame_menu.Menu('Options', 320, 240, theme=theme)

    csv_submenu = create_csv_menu()
    manual_submenu = create_manual_menu()
    wincondition =  win_conditions_menu()

    question_menu.add.button("Manual Input", manual_submenu, font_size=15)
    question_menu.add.button("Choose Default CSV", csv_submenu, font_size=15)
    question_menu.add.button("Load User CSV", user_csv, font_size=15)
    question_menu.add.button("Change Win Condition", wincondition,font_size=15)
    return question_menu

def create_csv_menu():
    theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    csv_menu = pygame_menu.Menu('Select CSV', 320, 240, theme=theme)

    csv_menu.add.button("Easy Mode", lambda: select_csv("data/questions/easy_mode.csv"), font_size=15)
    csv_menu.add.button("English", lambda: select_csv("data/questions/english.csv"), font_size=15)
    csv_menu.add.button("Geography", lambda: select_csv("data/questions/geography.csv"), font_size=15)
    csv_menu.add.button("Math", lambda: select_csv("data/questions/math.csv"), font_size=15)
    csv_menu.add.button("Psych", lambda: select_csv("data/questions/psych.csv"), font_size=15)

    return csv_menu

def create_manual_menu():
    theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    manual_menu = pygame_menu.Menu('Manual Input', 320, 240, theme=theme)
    
    question_input = manual_menu.add.text_input("Question: ", default="", font_size=11)
    answer_input = manual_menu.add.text_input("Correct Answer: ", default="", font_size=11)
    
    def handle_manual_input():
        global question_list
        question_text = question_input.get_value()
        answer_text = answer_input.get_value()
        wrong1_text = wrong1_input.get_value()
        wrong2_text = wrong2_input.get_value()
        wrong3_text = wrong3_input.get_value()
        
        if question_text and answer_text and wrong1_text and wrong2_text and wrong3_text:
            question_list.append([question_text, answer_text, wrong1_text, wrong2_text, wrong3_text])
            print(f"Added question: {question_text} -> {answer_text} with wrong answers: {wrong1_text}, {wrong2_text}, {wrong3_text}")
            question_input.set_value("")
            answer_input.set_value("")
            wrong1_input.set_value("")
            wrong2_input.set_value("")
            wrong3_input.set_value("")
        elif question_text and answer_text:
            question_list.append([question_text, answer_text])
            print(f"Added question: {question_text} -> {answer_text}")
            question_input.set_value("")
            answer_input.set_value("")
            wrong1_input.set_value("")
            wrong2_input.set_value("")
            wrong3_input.set_value("")
        else:
            print("Please enter both question and answer")
    
    manual_menu.add.button("Add Question", handle_manual_input, font_size=12)
    wrong1_input = manual_menu.add.text_input("Wrong Answer 1: ", default="", font_size=11)
    wrong2_input = manual_menu.add.text_input("Wrong Answer 2: ", default="", font_size=11)
    wrong3_input = manual_menu.add.text_input("Wrong Answer 3: ", default="", font_size=11)
    manual_menu.add.button("Save File", save_manual_questions, font_size=12)

    return manual_menu

def save_manual_questions():
    global question_list
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        from csv_unparser import save_to_csv
        save_to_csv(file_path, question_list)
        print(f"Saved {len(question_list)} questions to {file_path}")
    else:
        print("Save operation cancelled.")
    root.destroy()

def pause_menu():
    theme = pygame_menu.Theme(background_color=(50, 50, 50, 200),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    manual_menu = create_manual_menu()
    
    pause_menu = pygame_menu.Menu('', 320, 240, theme=theme)
    pause_menu.add.label("Paused", font_size=20, font_color=(255, 255, 255))
    pause_menu.add.vertical_margin(10)
    pause_menu.add.button("Resume", lambda: exit_menu(pause_menu), font_size=15)
    pause_menu.add.button("Add Questions", manual_menu, font_size=15)
    pause_menu.add.button("Quit", pygame_menu.events.EXIT, font_size=15)

    return pause_menu

def exit_menu(menu):
    menu.disable()
    menu._close()

def win_conditions_menu():
    theme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    win_condition = pygame_menu.Menu('Win Condtion:', 320, 240, theme=theme)
    def handle_manual_input():
        try:
           set_winquantity(box.get_value())
        except:
            print("INVALID!")
            pass

    box = win_condition.add.text_input("Quantity:", default="10", font_size=12)
    win_condition.add.button("Change Quantity:", lambda:(handle_manual_input()), font_size=12)
    win_condition.add.button("Correct", lambda:set_wincondition(1), font_size=12)
    win_condition.add.button("Score", lambda:set_wincondition(2), font_size=12)
    win_condition.add.button("Time", lambda:set_wincondition(3), font_size=12)
    win_condition.add.button("Answered", lambda:set_wincondition(4), font_size=12)
    win_condition.add.button("Endless.", lambda:set_wincondition(0), font_size=12)
    return win_condition


def set_wincondition(numb):
    global wincondition
    wincondition=numb

def set_winquantity(numb):
    global winquantity
    winquantity=int(numb)
    
    
def main_menu():
    theme = pygame_menu.Theme(background_color=(0, 0, 0, 0), title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE)
    
    menu = pygame_menu.Menu('', 320, 240, theme=theme)
    
    questions_submenu = create_questions_menu()
    
    logo_image = os.path.join('data', 'sprites', 'logo.png')
    play_button_image = os.path.join('data', 'sprites', 'play_button.png')
    questions_button_image = os.path.join('data', 'sprites', 'questions_button.png')
    
    menu.add.image(logo_image)
    menu.add.vertical_margin(20)
    menu.add.banner(pygame_menu.BaseImage(image_path=play_button_image), lambda: start_game())
    menu.add.vertical_margin(10)
    menu.add.banner(pygame_menu.BaseImage(image_path=questions_button_image), questions_submenu)

    return menu

if __name__ == "__main__":

    '''
    start_game()
    '''
    
    pygame.init()
    screen = pygame.display.set_mode((320, 240), pygame.RESIZABLE | pygame.SCALED)

    menu = main_menu()

    try:
        menu.mainloop(screen)
    except Exception as e:
        pass
    finally:
        pygame.quit()
        sys.exit()
    #'''
