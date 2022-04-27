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
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']
        self.mesa = gameinfo['mesa']

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
        
class Nombres_cartas_jugadores(pygame.sprite.Sprite):#Esto escribe los nombres en las cartas.
    def __init__(self, player):
      self.surface = pygame.surface([700,525])
      self.player = player
      self.n = 0
      self.fuente = pygame.font.Font(None,20)
      self.texto = ""
      self.render = self.fuente.render(self.texto,0,RED)
      self.contador = 0
      def set_mano(self):
          for i in self.player.mano:
              self.texto = str(i)
              if self.player.side == 0:
                  self.surface.blit(self.render,460,210+self.contador*60)
                  self.contador += self.contador
              else:
                  self.surface.blit(self.render,40,210+self.contador*60)
                  self.contador += self.contador
          self.contador = 0
          self.set_mano()
class Nombres_cartas_mesa(pygame.sprite.Sprite):#Esto escribe los nombres en las cartas.
    def __init__(self, mesa):
      self.surface = pygame.surface([700,525])
      self.mesa = mesa
      self.fuente = pygame.font.Font(None,20)
      self.texto = ""
      self.render = self.fuente.render(self.texto,0,RED)
      self.contador = 0
      def set_mesa(self):
          for i in self.player.mano:
              self.texto = str(i)
              if self.contador < 3:
                  self.surface.blit(self.render,125,310+self.contador*50)
                  self.contador += self.contador
              else:
                  self.surface.blit(self.render,225,310+((self.contador)%2)*50)
                  self.contador += self.contador
          self.contador = 0
          self.set_mesa()
    def __str__(self):
        return f"S<{self.player}>"

class Display():
    def __init__(self, game):
        self.game = game
        self.manos = [Nombres_cartas_jugadores(self.game.get_player(i)) for i in range(2)]
        self.mesa = Nombres_cartas_mesa(self.game.get_mesa)
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for mano  in self.manos:
            self.all_sprites.add(mano)
            self.paddle_group.add(mano)
        self.all_sprites.add(self.mesa)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.png')
        pygame.init()

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type != pygame.QUIT:
                events.append(event.type)
            elif event.type == pygame.QUIT:
                events.append("quit")
        return events


    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[UP_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (250, 30))
        text = font.render(f"{score[DOWN_PLAYER]}", 1, WHITE)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address):
    try:
        with Client((ip_address, 6321), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
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
    main(ip_address)