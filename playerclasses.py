class player:
    def __init__(self, cordx, cordy, maxhp, hp, score, containter = None):
        self.cords = [cordx,cordy]
        self.maxhp= maxhp
        self.hp = hp
        self.score = score
        self.container = container
        
    def hpmod(num):
        self.hp+=num
        if (self.hp>=maxhp):
            self.hp=maxhp
        if (self.hp<=0):
            die()
            
    def heal(num):
        hpmod(num)

    def hurt(num):
        hpmod(-num)

    def scoremod(num):
        self.score+=num

    def score(num):
        scoremod(num)

    def penalize(num):
        scoremod(-num)
        
    def die():
        raise NotImplementedError
        
class treasure(player):
    def __init__(self, cordx, cordy, score, container = None):
        self.cords = [cordx, cordy]
        self.hp = 1
        self.maxhp = 1
        self.score = score
        self.container = container

    def die():
        if (self.container !=None):
            container.remove(self)
        
    def whentouching(toucher):
        toucher.scoremod(score)
        die()

    def hpmod(num):
        self.hp=1

class 
