def create_random_enemy(cordx, cordy):
    # Make a random enemy at the given position
    enemy_types = [Salamander, Salamander, Salamander, Eyeball, Eyeball, Eyeball, Ogre]
    enemy_class = random.choice(enemy_types)
    return enemy_class(cordx, cordy)
