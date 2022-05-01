from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock, Condition, Semaphore
import traceback
import sys
import itertools, random

class Jugador():
    def __init__(self,side):
        self.side = side
        self.mano = [] #Cartas en mano
        self.cartas = [] #Cartas acumuludas
        self.puntos = 0
    
    def robar(self,x,baraja,mutex):
       mutex.acquire()
       for i in range(x):
           self.mano.append(baraja[0])
           baraja.pop(0)
       mutex.release()
        
class Game():
    def __init__(self,manager,baraja):
        self.running = Value('i', 1)
        self.jugadores=manager.list([Jugador(0), Jugador(1)])
        self.baraja = baraja
        self.mesa = manager.list([])
        self.mutex = Lock()
        self.turno = Value('i',0)

manager = Manager()
baraja = manager.list(list(itertools.product([1,2,3,4,5,6,7,8,9,10],['Espadas','Oros','Copas','Bastos']))) #Cambie los valores para que vayan de 0 a 10 para que las cartas sean mas faciles de manejar
random.shuffle(baraja)
game = Game(manager, baraja)
