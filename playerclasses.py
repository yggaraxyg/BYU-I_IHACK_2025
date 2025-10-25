import gameover

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

    def getscore():
        return self.score

    def gethp():
        return self.hp

    def getx():
        return self.cords[0]

    def gety():
        return self.cords[1]

    def setx(x):
        self.cords[0]=x

    def sety(y):
        self.cords[1]=y
        
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
            self.container.remove(self)
            del(self)
        
    def whentouching(toucher):
        toucher.scoremod(self.score)
        die()

    def hpmod(num):
        self.hp=1
    
class heart(player):
    def __init__(self, cordx, cordy, hp, container = None):
        self.cords = [cordx, cordy]
        self.hp = hp
        self.maxhp = hp
        self.score = 1
        self.container = container

    def die():
        if (self.container !=None):
            self.container.remove(self)
            del(self)
        
    def whentouching(toucher):
        toucher.hpmod(self.hp)
        die()

    def scoremod(num):
        self.score=1

    def hpmod(num):
        self.hp=self.hp

class 
