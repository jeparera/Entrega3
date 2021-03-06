from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import itertools, random

SIDESSTR = ["left", "right"]
SIZE = (700, 525)
LEFT_PLAYER = 0
RIGHT_PLAYER = 1


class Jugador():
    def __init__(self,side):
        self.side = side
        self.mano = []
        self.cartas = []
        self.puntos = 0
        self.escobas = 0
    
    def robar(self,x,baraja):
        for i in range(x):
            if len(baraja)>0:
                self.mano.append(baraja[0])
                baraja.pop(0)

    def get_hand(self):
        return self.mano
    
    def get_cartas(self):
        return self.cartas
    
    def jugar_recoger(self,cartasmesa,cartamano,mesa,baraja):
        p = 0
        cartamano_indice = 0
        while p == 0 and self.mano[cartamano_indice] != cartamano:
            cartamano_indice += 1
            if cartamano_indice == len(self.mano):
                p = 1
        if p == 0:
            suma15 = (self.mano[cartamano_indice])[0]
            cartasmesa_indices = []
            for j in range(len(mesa)):
                for k in range(len(cartasmesa)):
                    if mesa[j] == cartasmesa[k]:
                        cartasmesa_indices += [j]
            if len(cartasmesa_indices)==len(cartasmesa):
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
                    self.cartas.append(self.mano[cartamano_indice])
                    self.mano.pop(cartamano_indice)
                    for i in range(len(cartasmesa)):
                        if len(baraja)>0 and len(mesa)<4:
                            mesa.append(baraja[0])
                            baraja.pop(0)
                    self.robar(1, baraja)
                else:
                    self.puntos += (-4)
    def jugar_descartar(self,carta,mesa,baraja):
        i = 0
        p = 0
        while p == 0 and self.mano[i] != carta:
            i += 1
            if i == len(self.mano):
                p = 1
        if p == 0:
            mesa.append(self.mano[i])
            self.mano.pop(i)
            self.robar(1, baraja)
    
    def contar_sietesyoros(self):
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
        self.jugadores=manager.list([Jugador(LEFT_PLAYER), Jugador(RIGHT_PLAYER)])
        self.baraja = baraja
        self.mesa = manager.list([])
        self.mutex = Lock()
        self.turno = Value('i',0)
    
    def estado_baraja(self):
        return(len(self.baraja)!=0)
    
    def reponer_mesa(self):
        self.mutex.acquire()
        if len(self.mesa)<4:
            for i in range(4-len(self.mesa)):
                if self.estado_baraja():
                    self.mesa.append(self.baraja[0])
                    self.baraja.pop(0)
        self.mutex.release()
        
    def ultima_baza(self, player):
        self.mutex.acquire()
        p = self.jugadores[player]
        p.cartas += self.mesa
        p.mesa = []
        self.jugadores[player] = p
        self.mutex.release()

    def turno(self,jugador):
        return(self.turno.value==jugador)
        
    def contar_puntos_final(self): 
        jugador1 = self.jugadores[0]
        jugador2 = self.jugadores[1]
        puntos1 = jugador1.puntos
        puntos2 = jugador2.puntos
        puntos1 += len(jugador1.cartas)
        puntos2 += len(jugador2.cartas)
        if len(jugador1.cartas) < 10:
            puntos2 += 2
        if len(jugador2.cartas) < 10:
            puntos1 += 2
        [sietes1, oros1, sieteOros1] = jugador1.contar_sietesyoros()
        [sietes2, oros2, sieteOros2] = jugador2.contar_sietesyoros()
        puntos1 += (sietes1+oros1+sieteOros1+jugador1.escobas)
        puntos2 += (sietes2+oros2+sieteOros2+jugador2.escobas)
        if oros1 == 10:
            puntos1 += 1
        if oros2 == 10:
            puntos2 += 1
        if sietes1 == 4:
            puntos1 += 1
        if sietes2 == 4:
            puntos2 += 1    
        if oros1 > oros2:
            puntos1 += 1
        if oros2 > oros1:
            puntos2 += 1
        if sietes1 > sietes2:
            puntos1 += 1
        if sietes2 > sietes1:
            puntos2 += 1
        return [puntos1, puntos2]
            
    def ganador(self):
        [puntos_final1, puntos_final2] = self.contar_puntos_final()
        if puntos_final1<puntos_final2:
            print("Gana el jugador 2 con "+str(puntos_final2)+" puntos")
        elif puntos_final1>puntos_final2:
            print("Gana el jugador 1 con "+str(puntos_final1)+" puntos")
        else:
            print("Empate a "+str(puntos_final1)+" puntos")
        
    def stop(self):
        self.running.value = 0
        
    def get_mesa(self):
        return self.mesa[:]

    def is_running(self):
        return self.running.value == 1
    
    def get_info(self):
        info = {
            'mano_player1': self.jugadores[0].get_hand(),
            'cartas_player1': self.jugadores[0].get_cartas(),
            'mano_player2': self.jugadores[1].get_hand(),
            'cartas_player2': self.jugadores[1].get_cartas(),
            'mesa': self.get_mesa(),
            'baraja': len(self.baraja[:]),
            'is_running': self.is_running()       
            }
        return info
    
    def robar(self,x,player):
        self.mutex.acquire()
        p = self.jugadores[player]
        p.robar(x,self.baraja)
        self.jugadores[player] = p
        self.mutex.release()
        
    def jugar_recoger(self,cartasmesa,cartamano,player):
        self.mutex.acquire()
        p = self.jugadores[player]
        p.jugar_recoger(cartasmesa,cartamano,self.mesa,self.baraja)
        self.jugadores[player] = p
        self.mutex.release()
        
    def jugar_descartar(self,carta,player):
        self.mutex.acquire()
        p = self.jugadores[player]
        p.jugar_descartar(carta,self.mesa,self.baraja)
        self.jugadores[player] = p
        self.mutex.release()   
    
    def __str__(self):
        return f"G<{self.jugadores[LEFT_PLAYER]}:{self.jugadores[RIGHT_PLAYER]}:{self.running.value}>"

def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            k = 0
            commands = conn.recv()
            if commands == "next":
                conn.send(game.get_info())
            else:
                while commands[k] != "fin jugada":
                    while k < len(commands)-1:
                        if commands[k] == "quit":
                            game.stop()
                        elif commands[k] == "ultima baza":
                            game.ultima_baza(side)
                            game.stop()
                        elif commands[k] == "robar":
                            game.robar(1,side)
                        elif commands[k] =="descartar":
                            k += 1
                            while commands[k] != "fin jugada":
                                if type(commands[k]) == int:
                                    numero = commands[k]
                                    k += 1
                                elif commands[k] == "Espadas" or commands[k] == "Oros" or commands[k] == "Copas" or commands[k] == "Bastos":
                                    palo = commands[k]
                                    k += 1
                                else:
                                    k += 1 
                            carta = (numero,palo)
                            game.jugar_descartar(carta,side)
                        elif commands[k] =="recoger":
                            k += 1
                            while commands[k] != "mesa":
                                if type(commands[k]) == int:
                                    numero_mano = commands[k]
                                    k += 1
                                elif commands[k] == "Espadas" or commands[k] == "Oros" or commands[k] == "Copas" or commands[k] == "Bastos":
                                    palo_mano = commands[k]
                                    k += 1
                                else:
                                    k += 1
                            cartamano = (numero_mano,palo_mano)
                            cartasmesa = []
                            while commands[k] != "fin jugada":
                                j = 0
                                while j != 2:
                                    if type(commands[k]) == int:
                                        numero_mesa = commands[k]
                                        k += 1
                                        j += 1
                                    elif commands[k] == "Espadas" or commands[k] == "Oros" or commands[k] == "Copas" or commands[k] == "Bastos":
                                        palo_mesa = commands[k]
                                        k += 1
                                        j += 1
                                    else:
                                        k += 1
                                carta_mesa = (numero_mesa,palo_mesa)
                                cartasmesa += [carta_mesa]
                            game.jugar_recoger(cartasmesa,cartamano,side)
                            game.reponer_mesa()
                conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        game.ganador()
        print(f"Game ended")

def main(ip_address,port):
    manager = Manager()
    baraja = manager.list(list(itertools.product([1,2,3,4,5,6,7,8,9,10],['Espadas','Oros','Copas','Bastos'])))
    random.shuffle(baraja)
    try:
        with Listener((ip_address, port),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager, baraja)
            game.reponer_mesa()
            game.robar(3,LEFT_PLAYER)
            game.robar(3,RIGHT_PLAYER)
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