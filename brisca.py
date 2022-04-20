# -*- coding: utf-8 -*-
"""
Practica 3
"""
import itertools, random
player1 = []
player2 = []
puntos_1 = []
puntos_2 = []
mesa=[]
baraja = list(itertools.product([1,2,3,4,5,6,7,10,11,12],['Espadas','Oros','Copas','Bastos']))
random.shuffle(baraja)
print(baraja)
def robar(player,x):
    for i in range(x):
        player.append(baraja[0])
        baraja.pop(0)
def jugar(player,carta):
    mesa.append(player[carta])
    player.pop(carta)
def anadir_cartas_puntos(mesa,puntos):
    for i in mesa:
        x.append(i)
def ganador_turno(mesa):
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
            anadir_cartas_puntos(mesa,puntos_1)
            return(1)
        else:
            anadir_cartas_puntos(mesa,puntos_2)
            return(2)
    else:
        if mesa[0][1]==pinta:
            anadir_cartas_puntos(mesa,puntos_1)
            return(1)
        elif mesa[1][1]==pinta:
            anadir_cartas_puntos(mesa,puntos_2)
            return(2)
        else:
            anadir_cartas_puntos(mesa,puntos_1)
            return(1)
def contar_puntos():
    total_player1 = 0
    total_player2 = 0
    for i in puntos_1:
        if i[0]==1:
            total_player1 +=11
        elif i[0] == 3:
            total_player1 +=10
        elif i[0]==12:
            total_player1 +=4
        elif i[0]==11:
            total_player1 +=3
        elif i[0]==10:
            total_player1 +=2
    for i in puntos_2:
        if i[0]==1:
            total_player2 +=11
        elif i[0] == 3:
            total_player2 +=10
        elif i[0]==12:
            total_player2 +=4
        elif i[0]==11:
            total_player2 +=3
        elif i[0]==10:
            total_player2 +=2
    if total_player1<total_player2:
        return("gana el jugador 2 con",total_player2,"puntos")
    elif total_player1>total_player2:
        return("gana el jugador 1 con",total_player1,"puntos")
    else:
        return("empate")
            
print(baraja[0])
print(baraja[-1])

#Para iniciar el juego roban 3 cada uno#
robar(player1,3)
robar(player2,3)
print("pintan:",baraja[-1][1])
pinta = baraja[-1][1]
print(player1,player2)
#Juega primero el player1 eligiendo una de las 3 cartas que tiene (0,1,2)#
#Luego player2 pone su carta en la mesa y se determina el ganador.#
#Si gana player1 devuelve un 1 si no, un 2.#


