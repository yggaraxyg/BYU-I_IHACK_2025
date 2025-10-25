    
    def drop_loot(self):
        disable_colissions()
        death_treasure = treasure(self.cords[0], self.cords[1], self.score, self.container)

    def die():
        if (self.container !=None):
            drop_loot()
            self.container.remove(self)
            del(self)



def create_random_enemy(cordx, cordy):
    # Make a random enemy at the given position
    enemy_types = [Salamander, Salamander, Salamander, Eyeball, Eyeball, Eyeball, Ogre]
    enemy_class = random.choice(enemy_types)
    return enemy_class(cordx, cordy)
