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


SIDES = ["UP", "DOWN"]
SIDESSTR = ["UP", "DOWN"]

class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]
        self.puntos = 0
        self.mano = []
        
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

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[UP_PLAYER]}:{self.players[DOWN_PLAYER]}:{self.ball}>"

class cartas(pygame.sprite.Sprite):#La forma de las cartas siempre es la misma cambia las letras.
    def _init_(self):
        self.surface = pygame.surface([700,525])
        self.surface.fill(BLACK)
        pygame.draw.rect(self.surface,WHITE,[500,200,50,90])
        pygame.draw.rect(self.surface,WHITE,[500,260,50,90])
        pygame.draw.rect(self.surface,WHITE,[500,320,50,90])
        pygame.draw.rect(self.surface,WHITE,[165,300,50,90])
        pygame.draw.rect(self.surface,WHITE,[165,350,50,90])
        pygame.draw.rect(self.surface,WHITE,[265,300,50,90])
        pygame.draw.rect(self.surface,WHITE,[265,350,50,90])
        pygame.draw.rect(self.surface,WHITE,[0,260,50,90])
        pygame.draw.rect(self.surface,WHITE,[0,320,50,90])
        pygame.draw.rect(self.surface,WHITE,[0,200,50,90])
        
class Display():
    def __init__(self, game):
        self.game = game
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
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
                    event.append("fin jugada")
        return events


    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        mano0 = self.game.player[0].get_hand() 
        mano1 = self.game.player[1].get_hand()
        mesa = self.game.get_mesa()
        font = pygame.font.Font(None, 20)
        for i in range(3):
            text = font.render(str(mano0[i]),1,RED)
            self.screen.blit(text,460,210+i*60)
        for i in range(3):
            text = font.render(str(mano1[i]),1,RED)
            self.screen.blit(text,40,210+i*60)
        text = font.render(str(mesa[0]),1,RED)
        self.screen.blit(text,225,310)
        text = font.render(str(mesa[1]),1,RED)
        self.screen.blit(text,225,410)
        text = font.render(str(mesa[2]),1,RED)
        self.screen.blit(text,125,310)
        text = font.render(str(mesa[3]),1,RED)
        self.screen.blit(text,125,410)
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
            while game.is_running():
                events = display.analyze_events(side)
                if events[len(events)-1] != "fin jugada":
                        events += display.analyze_events(side)
                print(events)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
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