from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock, Condition
import traceback
import sys
import itertools, random

class Jugador():
    def __init__(self):
        self.mano=[]
        self.cartas = []
        self.puntos=0
        
    def robar(self,x,baraja):
        for i in range(x):
            self.hand.append(baraja[0])
            baraja.pop(0)
            
    def jugar(self,carta,mesa):
        mesa.append(self.mano[carta])
        self.mano.pop(carta)
        
    def anadir_cartas_puntos(self,mesa): #Esto hay que cambiarlo
        for i in mesa:
            self.cartas.append(i)

    def contar_puntos(self):
        for i in self.cartas:
            if i[0]==1:
                self.puntos +=11
            elif i[0] == 3:
                self.puntos +=10
            elif i[0]==12:
                self.puntos +=4
            elif i[0]==11:
                self.puntos +=3
            elif i[0]==10:
                self.puntos +=2

class Game():
    def __init__(self,manager,baraja):
        self.running = Value('i', 1)
        self.jugadores=manager.list([Jugador(), Jugador()])
        self.mesa = manager.list([])
        self.baraja = baraja
        self.pinta = baraja[-1][1]
        self.mutex = Lock()
        self.esperar = Condition(self.mutex)
        self.turno = Value('i',0)
    def turno_neutral(self):
        self.turno.value = -1
    def cambiar_turno(self):
        self.turno.value = ((self.turno.value+1)%2)
    def turno(self,jugador):
        return(self.turno.value==jugador)
    def ganador(self):
        total_player1 = self.jugadores[0].contar_puntos
        total_player2 = self.jugadores[1].contar_puntos
        if total_player1<total_player2:
            return("gana el jugador 2 con",total_player2,"puntos")
        elif total_player1>total_player2:
            return("gana el jugador 1 con",total_player1,"puntos")
        else:
            return("empate")
    def jugar_carta(self,jugador,carta):
        self.mutex.acquire()
        self.esperar.wait_for(self.turno)
        self.jugadores[jugador].jugar(carta)
        if len(self.mesa)==2:
            turno_neutral()
        else:
            cambiar_turno()
        self.mutex.release()
    def ganador_turno(self,mesa):
        valor1=mesa[0][0]
        valor2=mesa[1][0]
        if valor1==1:
            valor1=14
        if valor1==3:
            valor1=13
        if valor2==1:
            valor2=14
        if valor2==3:
            valor2=13
        if mesa[0][1]==mesa[1][1]:
            if valor1>valor2:
                return(1)
            else:
                return(2)
        else:
            if mesa[0][1]==self.pinta:
                return(1)
            elif mesa[1][1]==self.pinta:
                return(2)
            else:
                return(1)
    def stop(self):
        self.running.value = 0
    def get_info(self,jugador):
        info = {
            'mano player1': self.players.get_pos(),
            'mano player': self.players[RIGHT_PLAYER].get_pos(),
            'pos_ball': self.ball[0].get_pos(),
            'score': list(self.score),
            'is_running': self.running.value == 1
            }
        return(info)
def player(side, conn, game):
    try:
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "0":
                    game.jugar_carta(side,0,game.mesa)
                elif command == "1":
                    game.jugar_carta(side,1,game.mesa)
                elif command == "2":
                    game.jugar_carta(side,2,game.mesa)
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
    mesa = []
    baraja = manager.list(list(itertools.product([1,2,3,4,5,6,7,10,11,12],['Espadas','Oros','Copas','Bastos'])))
    random.shuffle(baraja)
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=Jugador,
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

    main(ip_address)