from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import itertools, random

mesa = []
baraja = list(itertools.product([1,2,3,4,5,6,7,10,11,12],['Espadas','Oros','Copas','Bastos']))
random.shuffle(baraja)

class Jugador():
    def __init__(self):
        self.mano=[]
        self.puntos=[]
        
    def robar(self,x):
        for i in range(x):
            self.hand.append(baraja[0])
            baraja.pop(0)
            
    def jugar(self,carta):
        mesa.append(self.mano[carta])
        player.pop(carta)
        
    def anadir_cartas_puntos(mesa,puntos): #Esto hay que cambiarlo
        for i in mesa:
            x.append(i)

    def contar_puntos(self):
        for i in puntos_1:
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

class Juego():
    def __init__(self):
        self.jugadores=[Jugador(), Jugador()]
        
    def ganador(self):
        total_player1 = self.jugadores[0].contar_puntos
        total_player2 = self.jugadores[1].contar_puntos
        if total_player1<total_player2:
            return("gana el jugador 2 con",total_player2,"puntos")
        elif total_player1>total_player2:
            return("gana el jugador 1 con",total_player1,"puntos")
        else:
            return("empate")
        
    def ganador_turno(self):
        valor1=0
        valor2=0
        if mesa[0][0]==1:
            valor1=11
        if mesa[0][0]==3:
            valor1=10
        if mesa[1][0]==1:
            valor1=11
        if mesa[1][0]==3:
            valor1=10
        if mesa[0][1]==mesa[1][1]:
            if valor1>valor2:
                anadir_cartas_puntos(mesa,self.jugadores[0].puntos)
                return(1)
            else:
                anadir_cartas_puntos(mesa,self.jugadores[1].puntos)
                return(2)
        else:
            if mesa[0][1]==pinta:
                anadir_cartas_puntos(mesa,self.jugadores[0].puntos)
                return(1)
            elif mesa[1][1]==pinta:
                anadir_cartas_puntos(mesa,self.jugadores[1].puntos)
                return(2)
            else:
                anadir_cartas_puntos(mesa,self.jugadores[0].puntos)
                return(1)
        