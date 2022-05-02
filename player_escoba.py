from multiprocessing.connection import Client
import traceback
import pygame
import sys, os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

UP_PLAYER = 0
DOWN_PLAYER = 1
PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 0
PLAYER_WIDTH = 0
FPS = 60


SIDES = ["LEFT", "RIGHT"]
SIDESSTR = ["LEFT", "RIGHT"]

class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]
        self.puntos = 0
        self.mano = []
        self.cartas = []
        
    def get_hand(self):
        return self.mano
 
    def get_cartas(self):
        return self.cartas
    
    def get_puntos(self):
        return self.puntos
    
    def __str__(self):
        return f"P<{SIDES[self.side], self.mano}>"

class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.score = [0,0]
        self.mesa = []
        self.running = True
    
    def get_player(self, side):
        return self.players[side]
    
    def get_score(self):
        return self.score
    
    def get_mesa(self):
        return self.mesa
    
    def set_score(self, score):
        self.score = score

    def update(self, gameinfo):
        self.running = gameinfo['is_running']
        self.mesa = gameinfo['mesa']
        self.players[0].mano = gameinfo['mano_player1']
        self.players[1].mano = gameinfo['mano_player2']
        self.players[0].cartas = gameinfo['cartas_player1']
        self.players[1].cartas = gameinfo['cartas_player2']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[UP_PLAYER]}:{self.players[DOWN_PLAYER]}:{self.ball}>"
        
class Display():
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.jpeg')
        pygame.init()

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append("quit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_KP_MINUS:
                    events.append("descartar")
                elif event.key == pygame.K_KP_PLUS:
                    events.append("recoger")
                elif event.key == pygame.K_KP_DIVIDE:
                    events.append("mesa")
                elif event.key == pygame.K_KP0:
                    events.append(10)
                elif event.key == pygame.K_KP1:
                    events.append(1)
                elif event.key == pygame.K_KP2:
                    events.append(2)
                elif event.key == pygame.K_KP3:
                    events.append(3)
                elif event.key == pygame.K_KP4:
                    events.append(4)
                elif event.key == pygame.K_KP5:
                    events.append(5)
                elif event.key == pygame.K_KP6:
                    events.append(6)
                elif event.key == pygame.K_KP7:
                    events.append(7)
                elif event.key == pygame.K_KP8:
                    events.append(8)
                elif event.key == pygame.K_KP9:
                    events.append(9)
                elif event.key == pygame.K_e:
                    events.append("Espadas")
                elif event.key == pygame.K_o:
                    events.append("Oros")
                elif event.key == pygame.K_c:
                    events.append("Copas")
                elif event.key == pygame.K_b:
                    events.append("Bastos")
                elif event.key == pygame.K_f:
                    events.append("fin jugada")
                elif event.key == pygame.K_u:
                    events.append("ultima baza")
                elif event.key == pygame.K_r:
                    events.append("robar")
        return events

    def refresh(self):
        self.screen.blit(self.background, (0, 0))
        manoder = self.game.players[0].get_hand() 
        manoizq = self.game.players[1].get_hand()
        mesa = self.game.get_mesa()
        font = pygame.font.Font(None, 20)
        pygame.draw.rect(self.screen,WHITE,[600,200,90,50])
        pygame.draw.rect(self.screen,WHITE,[600,260,90,50])
        pygame.draw.rect(self.screen,WHITE,[600,320,90,50])
        pygame.draw.rect(self.screen,WHITE,[250,230,90,50])
        pygame.draw.rect(self.screen,WHITE,[250,290,90,50])
        pygame.draw.rect(self.screen,WHITE,[350,230,90,50])
        pygame.draw.rect(self.screen,WHITE,[350,290,90,50])
        pygame.draw.rect(self.screen,WHITE,[10,260,90,50])
        pygame.draw.rect(self.screen,WHITE,[10,320,90,50])
        pygame.draw.rect(self.screen,WHITE,[10,200,90,50])
        for i in range(len(mesa)):
            if i%2==0:
                text = font.render(str(mesa[i]),1,RED)
                self.screen.blit(text,(270+(i)*50,250))
            else:
                text = font.render(str(mesa[i]),1,RED)
                self.screen.blit(text,(270+(i-1)*50,310))
        for i in range(len(manoizq)):
            text = font.render(str(manoizq[i]),1,RED)
            self.screen.blit(text,(620,220+i*60))
        for i in range(len(manoder)):
            text = font.render(str(manoder[i]),1,RED)
            self.screen.blit(text,(30,220+i*60))
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address,port):
    try:
        with Client((ip_address, port), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            display.refresh()
            display.tick()
            while game.is_running():
                events = display.analyze_events(side)
                while len(events) == 0:
                    events = display.analyze_events(side)
                if len(events) > 0:
                    while events[-1] != "fin jugada":
                        new = display.analyze_events(side)
                        if new != []:
                            events += new
                            print(events)
                conn.send(events)
                for ev in events:
                    if ev == 'quit':
                        game.stop()
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    if len(sys.argv)>1:
        port = int(sys.argv[2])
    main(ip_address, port)