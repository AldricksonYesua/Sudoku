# Proyecto: SUDOKU
# Curso: Taller de Programacion - TEC
# Autor: Aldrickson Yesua
# Fecha: Mayo 2026
# Descripcion: Juego de Sudoku con interfaz grafica (tkinter)

import tkinter as tk
from tkinter import messagebox
import json
import random
from collections import deque
from datetime import datetime
import os


NUMEROS = ['1','2','3','4','5','6','7','8','9']
LETRAS  = ['A','B','C','D','E','F','G','H','I']

NIVELES = ['facil', 'intermedio', 'dificil']

ARCHIVO_CONFIG    = 'sudoku2026configuracion.json'
ARCHIVO_BITACORA  = 'sudoku2026_bitacora_jugadas.json'
ARCHIVO_GUARDADO  = 'sudoku2026juegoactual.json'
ARCHIVO_PARTIDAS  = 'sudoku2026partidas.json'


# ESTRUCTURAS DE DATOS DEL TABLERO


def crear_tablero_vacio():
    #Retorna una matriz 9x9 inicializada en cero.
    return [[0]*9 for _ in range(9)]

def crear_matriz_fijas():
    #Retorna una matriz 9x9 de False (ninguna casilla es fija).
    return [[False]*9 for _ in range(9)]

# =============================================================
# PILAS (TDA) - usando collections.deque
# =============================================================

def crear_pila():
    # Retorna una pila vacia implementada con deque
    return deque()

def pila_push(pila, elemento):
    # Agrega un elemento al tope de la pila
    pila.append(elemento)

def pila_pop(pila):
    # Saca y retorna el elemento del tope de la pila
    # Cada elemento es una tupla (fila, columna, valor)
    return pila.pop()

def pila_vacia(pila):
    # Retorna True si la pila esta vacia
    return len(pila) == 0


# =============================================================
# LOGICA DE VALIDACIONES
# =============================================================

def es_valido_fila(tablero, fila, valor):
    # Verifica que el valor no este repetido en la fila
    for col in range(9):
        if tablero[fila][col] == valor:
            return False
    return True

def es_valido_columna(tablero, columna, valor):
    # Verifica que el valor no este repetido en la columna
    for fila in range(9):
        if tablero[fila][columna] == valor:
            return False
    return True

def es_valido_cuadricula(tablero, fila, columna, valor):
    # Verifica que el valor no este repetido en la subcuadricula 3x3
    inicio_fila = (fila // 3) * 3
    inicio_col  = (columna // 3) * 3
    for i in range(inicio_fila, inicio_fila + 3):
        for j in range(inicio_col, inicio_col + 3):
            if tablero[i][j] == valor:
                return False
    return True

def validar_jugada(tablero, fijas, fila, columna, valor):
    # Valida una jugada completa
    # Retorna (True, '') si es valida o (False, mensaje) si no lo es
    if fijas[fila][columna]:
        return False, "JUGADA NO ES VALIDA PORQUE ESTE ES UN ELEMENTO FIJO"
    if not es_valido_fila(tablero, fila, valor):
        return False, "JUGADA NO ES VALIDA PORQUE EL ELEMENTO YA ESTA EN LA FILA"
    if not es_valido_columna(tablero, columna, valor):
        return False, "JUGADA NO ES VALIDA PORQUE EL ELEMENTO YA ESTA EN LA COLUMNA"
    if not es_valido_cuadricula(tablero, fila, columna, valor):
        return False, "JUGADA NO ES VALIDA PORQUE EL ELEMENTO YA ESTA EN LA CUADRICULA"
    return True, ""

def juego_completo(tablero):
    # Retorna True si todas las casillas estan llenas (sin ceros)
    for fila in range(9):
        for col in range(9):
            if tablero[fila][col] == 0:
                return False
    return True

