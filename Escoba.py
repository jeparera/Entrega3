from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock, Condition, Semaphore
import traceback
import sys
import itertools, random

class Jugador():
    def __init__(self):
        self.mano = [] #Cartas en mano
        self.cartas = [] #Cartas acumuludas
        self.puntos = 0
        self.escobas = 0 #Contador de escobas para sumarlo al final
    
    def robar(self,x,baraja):
        for i in range(x):
            self.cartas.append(baraja[0])
            baraja.pop(0)
    
    def get_hand(self):
        return self.mano
    
    def get_cartas(self):
        return self.cartas
    
    def jugar_recoger(self,cartasmesa,cartamano,mesa): #Esta función sirve para elegir las bazas (Ademas, si no suman quince te penaliza y si barres te suma escoba)       
        suma15 = (self.mano[cartamano])[0]
        for i in cartasmesa:
            suma15 += (mesa[i])[0]
        if suma15 == 15:
            for i in cartasmesa:    
                self.cartas.append(mesa[i])
                mesa.pop(i)
            if len(mesa) == 0:
                self.escobas += 1
            self.cartas.append(self.mano[cartamano])
            self.mano.pop(cartamano)
        else:
            self.puntos += (-4)
            
    def jugar_descartar(self,carta,mesa): #Esta función sirve para cuando no tienes sumas de 15 dejar una carta en la mesa
        mesa.append(self.mano[carta])
        self.mano.pop(carta)
    
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

class Game():
    def __init__(self,manager,baraja,semaforo):
        self.running = Value('i', 1)
        self.jugadores=manager.list([Jugador(), Jugador()])
        self.mesa = manager.list([])
        self.baraja = baraja
        self.mutex = Lock()
        self.esperar = Condition(self.mutex)
        self.turno = Value('i',0)
    
    def estado_baraja(self):
        return(len(self.baraja)!=0)
    
    def ultima_baza(self, jugador): #Las cartas que quedan al final de la partida en la mesa se las lleva el jugador que hizo la última baza
        self.cartas += self.mesa
    
    def turno_neutral(self):
        self.turno.value = -1
    
    def cambiar_turno(self):
        self.turno.value = ((self.turno.value+1)%2)
    
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
    
    def jugar_carta(self,jugador,carta,semaforo):
        self.mutex.acquire()
        self.esperar.wait_for(self.turno)
        self.jugadores[jugador].jugar(carta)
        if len(self.mesa)==2:
            self.turno_neutral()
            semaforo.release()
        else:
            self.cambiar_turno()
        self.mutex.release()
    
    def stop(self):
        self.running.value = 0
    
    def get_info(self):
        info = {
            'mano player1': self.jugadores[0].get_hand(),
            'mano player2': self.jugadores[1].get_hand(),
            'cartas player1': self.jugadores[0].get_cartas(),
            'cartas player2': self.jugadores[1].get_cartas(),
            'mesa': self.mesa,
            'is_running': self.running.value == 1
            }
        return(info)

def aux(game,semaforo):
    try:
        while game.is_running():
            semaforo.acquire()
            ganador = game.ganador_turno(game.mesa)
            if ganador == 1 and game.estado_baraja():
                game.jugadores[0].robar(1,game.baraja)
                game.turno.value=0
            elif ganador == 2 and game.estado_baraja():
                game.jugadores[1].robar(1,game.baraja)
                game.turno.value=1
            elif not(game.estado_baraja()):
                game.turno.value=(ganador-1)
    except:
        traceback.print_exc()

def player(side, conn, game,semaforo):
    try:
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "0":
                    game.jugar_carta(side,0,game.mesa,semaforo)
                elif command == "1":
                    game.jugar_carta(side,1,game.mesa,semaforo)
                elif command == "2":
                    game.jugar_carta(side,2,game.mesa,semaforo)
                elif command == "vacio":
                    game.ganador()
                    game.stop()
                elif command == "quit":
                    game.stop()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

def main(ip_address):
    manager = Manager()
    baraja = manager.list(list(itertools.product([1,2,3,4,5,6,7,8,9,10],['Espadas','Oros','Copas','Bastos']))) #Cambie los valores para que vayan de 0 a 10 para que las cartas sean mas faciles de manejar
    random.shuffle(baraja)
    semaforo = Semaphore(0)
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager, baraja)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game,semaforo))
                n_player += 1
                if n_player == 2:
                    aux = 0
                    aux = Process(target=aux,
                                  args=(game,semaforo))
                    aux.start()
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager,baraja,semaforo)
    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)