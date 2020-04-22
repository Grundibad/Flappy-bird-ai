import pygame
import random
import time
import neat
import os
import pickle
pygame.init()
display_width = 800
display_height = 302
generace = 0




gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
background = pygame.image.load("background.png")
roura = pygame.image.load("pipe.png")
roura2 = pygame.image.load("pipe2.png")
flappy_bird = pygame.image.load("bird.jpeg")



class Bird():
    def __init__(self):
        self.y = 150
        self.x = 100
        self.obrazek = flappy_bird
        self.crashed = False
        self.cas = 0
    def jump(self):
        self.cas = 0
    def nakresli(self):
        gameDisplay.blit(self.obrazek, (self.x, self.y))
    def y_souradnice(self):
        v = 4
        self.y = self.y - (v - 10*self.cas) + (5 * self.cas**2)
        if self.y > 278:
            self.y = 278
    def do_it(self):
        self.y_souradnice()
        self.nakresli()
    def misto(self):
        return (self.x, self.y)
    def ptak(self):
        return pygame.rect.Rect(self.misto(), (20, 15))
    def check(self, objekty, crashed, ptaci, nets, ge, x):
        zeme = 278
        roura1 = objekty[0].roura()
        if self.y >= zeme:
            self.crashed = True
            ge[x].fitness -= 2
            return crash(crashed, ptaci, nets, ge, x)
        elif self.y <0:
            self.crashed = True
            ge[x].fitness -= 2
            return crash(crashed, ptaci, nets, ge, x)
        elif roura1.colliderect(self.ptak()):
            self.crashed = True
            ge[x].fitness -= 1
            return crash(crashed, ptaci, nets, ge, x)
        elif objekty[0].roura2().colliderect(self.ptak()):
            self.crashed = True
            ge[x].fitness -= 1
            return crash(crashed, ptaci, nets, ge, x)
        else:
            return crashed
            

class Pipe():
    def __init__(self, x):
        self.y = random.randint(94,233)
        self.x = x
        self.obrazek = roura
        self.obrazek_2 = roura2
        self.rozmery = (54, 310)
    def posun(self, posun):
        self.x -= posun
    def nakresli(self):
        gameDisplay.blit(self.obrazek, (self.x, self.y))
    def misto(self):
        return (self.x, self.y)
    def misto2(self):
        return (self.x, self.y-364)
    def roura(self):
        return pygame.rect.Rect(self.misto(), self.rozmery)
    def roura2(self): 
        return pygame.rect.Rect(self.misto2(),self.rozmery)
    def do_it(self, posun):
        self.posun(posun)
        self.nakresli()
        gameDisplay.blit(self.obrazek_2, (self.x, self.y-364))
    def __str__(self):
        return "x: {0}, y:{1} \n".format(self.x,self.y)
        
class Pipes():
    def __init__(self):
        self.roury = []
    def napln(self):
        x = 800
        for i in range(4):
            self.roury.append(Pipe(x))
            x += 218
    def prehod(self):
        if self.roury[0].x <= -54:
            self.roury.remove(self.roury[0])
            self.roury.append(Pipe(800))
    def do_it(self, posun):
        self.prehod()
        for roura in self.roury:
            roura.do_it(posun)
    def get_roury(self):
        return self.roury




def pozadi(xpozadi, xpozadi2, posun):
    
    if xpozadi <= -800:
        xpozadi = 800
    elif xpozadi2 <= -800:
        xpozadi2 = 800
    gameDisplay.blit(background, (xpozadi,0))
    gameDisplay.blit(background, (xpozadi2,0))
    xpozadi -= posun
    xpozadi2 -= posun
    return xpozadi, xpozadi2


def score(roury, skore, ptaci, ge):
    if roury.roury[0].x <45 and roury.roury[0].x > 40:
        skore += 1
        for x,ptaci in enumerate(ptaci):
            ge[x].fitness += 2
    return skore

def checking(roury, crashed, ptaci, nets, ge):
    for x, ptak in enumerate(ptaci):
        crashed = ptak.check(roury, crashed, ptaci, nets, ge, x) 
    return crashed 

def crash(crashed, ptaci, nets, ge, x):
    ptaci.pop(x)
    nets.pop(x)
    ge.pop(x)
    if ptaci == []:
        crashed = True
    return crashed

def napis(text, x, y):
    myfont = pygame.font.SysFont("Arial", 30)
    letter = myfont.render(text,1,(0,0,0))
    gameDisplay.blit(letter,(x,y))
    
def game(genomes, config):
    global generace
    generace += 1
    xpozadi = 0
    xpozadi2 = 800
    skore = 0
    posun = 4

    nets = []
    ge = []
    ptaci = []

    for _,g in genomes:

        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        ptaci.append(Bird())
        g.fitness = 0
        ge.append(g)
    print("haha",_,"hahaa", g, "haha")

    roury = Pipes()
    roury.napln()
    
    crashed = False
    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
                pygame.quit()
                quit
        dt = clock.tick(50)/ 1000
        pipe_ind = 0
        if roury.roury[0].x < 46:
            pipe_ind = 1
        crashed = checking(roury.roury, crashed, ptaci, nets, ge)
        skore= score(roury, skore, ptaci, ge)


        xpozadi, xpozadi2 = pozadi(xpozadi, xpozadi2, posun)
        roury.do_it(posun)
        napis("Skore: {}".format(skore), 700, 10)
        napis("Generace: {}".format(generace), 10, 10)
        napis("Počet: {}".format(len(ptaci)),10, 30)
        
        for x, ptak in enumerate(ptaci):
            output = nets[x].activate(( abs(ptak.y -roury.roury[pipe_ind].y), abs(ptak.y - (roury.roury[pipe_ind].y - 54))))
            
            ptak.cas += dt
            ge[x].fitness += 0.01
            ptak.do_it()
        
            if output[0] > 0.5:
                ptak.jump()
        pygame.display.update()
        

        

        

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(game,3)
    with open("winner.pkl", "wb") as output:
        pickle.dump(winner, output)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-for-flappy-bird.txt")
    run(config_path)

