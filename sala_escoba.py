from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock, Condition, Semaphore
import traceback
import sys
import itertools, random

SIDESSTR = ["up", "down"]
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

class Jugador():
    def __init__(self,side):
        self.side = side
        self.mano = [] #Cartas en mano
        self.cartas = [] #Cartas acumuludas
        self.puntos = 0
        self.escobas = 0 #Contador de escobas para sumarlo al final
    
    def robar(self,x,baraja,mutex):
        mutex.acquire()
        for i in range(x):
            self.mano.append(baraja[0])
            baraja.pop(0)
        mutex.release()
    def get_hand(self):
        return self.mano
    
    def get_cartas(self):
        return self.cartas
    
    def jugar_recoger(self,cartasmesa,cartamano,mesa,mutex): #Esta función sirve para elegir las bazas (Ademas, si no suman quince te penaliza y si barres te suma escoba)       
        mutex.acquire()
        cartamano_indice = 0
        while self.mano[cartamano_indice] != cartamano:
            cartamano_indice += 1
        suma15 = (self.mano[cartamano_indice])[0]
        cartasmesa_indices = []
        for j in range(len(mesa)):
            for k in range(len(cartasmesa)):
                if mesa[j] == cartasmesa[k]:
                    cartasmesa_indices += [j]
        for k in cartasmesa_indices:
            suma15 += (mesa[k])[0]
        if suma15 == 15:
            n = []
            for k in cartasmesa_indices:
                self.cartas.append(mesa[k])
                n.append(k)
            n_sorted = sorted(n,reverse=True)
            for k in n_sorted:
                mesa.pop(k)
            if len(mesa) == 0:
                self.escobas += 1
            self.cartas.append(self.mano[i])
            self.mano.pop(i)
        else:
            self.puntos += (-4)
        mutex.release()
        
    def jugar_descartar(self,carta,mesa,baraja,mutex): #Esta función sirve para cuando no tienes sumas de 15 dejar una carta en la mesa
        mutex.acquire
        i = 0
        while self.mano[i] != carta:
            i += 1
        mesa.append(self.mano[i])
        self.mano.pop(i)
        self.robar(1, baraja)
        mutex.release()
    def anadir_cartas_puntos(self,mesa):
        for i in mesa:
            self.cartas.append(i)
    
    def contar_sietesyoros(self): #Esta función se utiliza en la clase game para hacer la comparación de los puntos
        sietes = 0
        oros = 0
        sieteOros = 0
        for i in self.cartas:
            if i[1]=='Oros':
                oros +=1
                if i[0] == 7:
                    sieteOros = 1
            if i[0] == 7:
                sietes +=1
        return [sietes,oros,sieteOros]
    
    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.puntos}>"

class Game():
    def __init__(self,manager,baraja):
        self.running = Value('i', 1)
        self.jugadores=manager.list([Jugador(0), Jugador(1)])
        self.baraja = baraja
        self.mesa = manager.list([])
        self.mutex = Lock()
        self.turno = Value('i',0)
    
    def estado_baraja(self):
        return(len(self.baraja)!=0)
    def reponer_mesa(self):
        self.mutex.acquire()
        if len(self.mesa)<4 and self.estado_baraja():
            for i in range(4-len(self.mesa)):
                self.mesa.append(self.baraja[0])
                self.baraja.pop(0)
        self.mutex.release()
    def ultima_baza(self, jugador): #Las cartas que quedan al final de la partida en la mesa se las lleva el jugador que hizo la última baza
        self.jugadores[jugador].cartas += self.mesa

    def turno(self,jugador):
        return(self.turno.value==jugador)
        
    def contar_puntos_final(self): #Esta funcion cuenta los puntos de ambos al final y los devuelve en un vector (esta funcion la meto aqui y no en la clase jugador porque tienes que comparar las cartas de ambos para contar los puntos)
        jugador1 = self.jugadores[0]
        jugador2 = self.jugadores[1]
        jugador1.puntos += len(jugador1.cartas)
        jugador2.puntos += len(jugador2.cartas)
        if len(jugador1.cartas) < 10:
            jugador2.puntos += 2
        if len(jugador2.cartas) < 10:
            jugador1.puntos += 2
        [sietes1, oros1, sieteOros1] = jugador1.contar_sietesyoros()
        [sietes2, oros2, sieteOros2] = jugador2.contar_sietesyoros()
        jugador1.puntos += (sietes1+oros1+sieteOros1+jugador1.escobas)
        jugador2.puntos += (sietes2+oros2+sieteOros2+jugador2.escobas)
        if oros1 == 10:
            jugador1.puntos += 1
        if oros2 == 10:
            jugador2.puntos += 1
        if sietes1 == 4:
            jugador1.puntos += 1
        if sietes2 == 4:
            jugador2.puntos += 1    
        if oros1 > oros2:
            jugador1.puntos += 1
        if oros2 > oros1:
            jugador2.puntos += 1
        if sietes1 > sietes2:
            jugador1.puntos += 1
        if sietes2 > sietes1:
            jugador2.puntos += 1
            
    def ganador(self): #Esta funcion devuelve un print con el ganador despues de contar los puntos
        self.contar_puntos_final()
        puntos_final1 = self.jugadores[0].puntos
        puntos_final2 = self.jugadores[1].puntos
        if puntos_final1<puntos_final2:
            return("gana el jugador 2 con",puntos_final2,"puntos")
        elif puntos_final1>puntos_final2:
            return("gana el jugador 1 con",puntos_final1,"puntos")
        else:
            return("empate")
    def stop(self):
        self.running.value = 0
    def get_mesa(self):
        l = []
        for i in self.mesa[:]:
            l.append(i)
        return(l)

    def is_running(self):
        return self.running.value == 1
    
    def get_info(self):
        info = {
            'mano_player1': self.jugadores[0].get_hand(),
            'mano_player2': self.jugadores[1].get_hand(),
            'mesa': self.get_mesa(),
            'is_running': self.is_running()
            }
        return info
    
    
    def __str__(self):
        return f"G<{self.jugadores[UP_PLAYER]}:{self.jugadores[DOWN_PLAYER]}:{self.running.value}>"

def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "quit":
                    game.stop()
                elif command =="descartar":
                    commandAUX = ""
                    while commandAUX != "fin jugada":
                        commandAUX = conn.recv()
                        if type(commandAUX) == int:
                            numero = commandAUX
                        elif commandAUX == "Espadas" or commandAUX == "Oros" or commandAUX == "Copas" or commandAUX == "Bastos":
                            palo = commandAUX
                    carta = (numero,palo)
                    game.jugadores[side].jugar_descartar(carta,game.mesa,game.baraja,game.mutex)
                elif command =="recoger":
                    commandAUX = ""
                    while commandAUX != "mesa":
                        commandAUX = conn.recv()
                        if type(commandAUX) == int:
                            numero_mano = commandAUX
                        elif commandAUX == "Espadas" or commandAUX == "Oros" or commandAUX == "Copas" or commandAUX == "Bastos":
                            palo_mano = commandAUX
                    carta_mano = (numero_mano,palo_mano)
                    cartas_mesa = []
                    numero_mesa = 12 #No en {0,...,10}
                    palo_mesa = "" #No un palo
                    while commandAUX != "fin jugada":
                        commandAUX = conn.recv()
                        if type(commandAUX) == int:
                            numero_mesa = commandAUX
                        elif commandAUX == "Espadas" or commandAUX == "Oros" or commandAUX == "Copas" or commandAUX == "Bastos":
                            palo_mesa = commandAUX
                        carta_mesa = [numero_mesa,palo_mesa]
                        if numero_mesa != 12 and palo_mesa != "":
                            cartas_mesa += [carta_mesa]
                    game.jugadores[side].jugar_recoger(cartas_mesa,carta_mano,game.mesa,game.mutex)
                    game.reponer_mesa()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

def main(ip_address,port):
    manager = Manager()
    baraja = manager.list(list(itertools.product([1,2,3,4,5,6,7,8,9,10],['Espadas','Oros','Copas','Bastos']))) #Cambie los valores para que vayan de 0 a 10 para que las cartas sean mas faciles de manejar
    random.shuffle(baraja)
    try:
        with Listener((ip_address, port),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager, baraja)
            game.reponer_mesa()
            game.jugadores[0].robar(3,game.baraja,game.mutex)
            game.jugadores[1].robar(3,game.baraja,game.mutex)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager,baraja)
    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    if len(sys.argv)>2:
        port = int(sys.argv[2])
    main(ip_address,port)