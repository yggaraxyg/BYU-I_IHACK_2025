    
    def move_towards_player(self, player_x, player_y):
        # Basic movement towards player
        direction = pygame.Vector2(player_x, player_y) - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction*speed
            self.rect.center = self.pos
    
    def drop_loot(self):
        disable_colissions()
        death_treasure = treasure(self.cords[0], self.cords[1], self.score, self.container)

    def die():
        if (self.container !=None):
            drop_loot()
            self.container.remove(self)
            del(self)


class Salamander(Enemy):
    # Salamander - moves toward player
    def __init__(self, cordx, cordy, container = None):
        super().__init__(cordx, cordy, 20, 20, 40, 1, "data/sprites/salamander.png", container = None)

    def update(self, player_pos):
        self.move_towards_player(player_pos)

class Eyeball(Enemy):
    # Eyeball - sits in one spot
    def __init__(self, cordx, cordy, container = None):
        super().__init__(cordx, cordy, 50, 50, 40, 1, "data/sprites/florb.png", container = None)

class Ogre(Enemy):
    # Ogre - Moves slowly, very tough.
    def __init__(self, cordx, cordy, container = None):
        super().__init__(cordx, cordy, 400, 400, 500, 0.25, "data/sprites/florb.png", container = None)

    def update(self, player_pos):
        self.move_towards_player(player_pos)


def create_random_enemy(cordx, cordy):
    # Make a random enemy at the given position
    enemy_types = [Salamander, Salamander, Salamander, Eyeball, Eyeball, Eyeball, Ogre]
    enemy_class = random.choice(enemy_types)
    return enemy_class(cordx, cordy)
