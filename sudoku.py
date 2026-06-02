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


def cargar_configuracion():
    # Carga la configuracion desde el archivo, si no existe crea una por defecto
    config_default = {
        "nivel": "facil",
        "reloj": {
            "tipo": "cronometro",
            "horas": 0,
            "minutos": 0,
            "segundos": 0
        },
        "top x": 3,
        "elementos": "numeros"
    }
    if not os.path.exists(ARCHIVO_CONFIG):
        with open(ARCHIVO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(config_default, f, indent=4)
        return config_default
    with open(ARCHIVO_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def obtener_partida_aleatoria(nivel):
    # Abre el archivo de partidas y selecciona una al azar del nivel indicado
    # Retorna la partida o None si no hay partidas de ese nivel
    if not os.path.exists(ARCHIVO_PARTIDAS):
        return None
    with open(ARCHIVO_PARTIDAS, 'r', encoding='utf-8') as f:
        partidas = json.load(f)
    if nivel not in partidas or len(partidas[nivel]) == 0:
        return None
    indice = random.randint(0, len(partidas[nivel]) - 1)
    return partidas[nivel][indice]



class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SUDOKU - TEC")
        self.root.resizable(False, False)

        # variables del juego
        self.tablero        = crear_tablero_vacio()
        self.fijas          = crear_matriz_fijas()
        self.tablero_orig   = crear_tablero_vacio()
        self.pila_realizadas  = crear_pila()
        self.pila_eliminadas  = crear_pila()
        self.juego_iniciado = False
        self.elemento_seleccionado = None
        self.config = cargar_configuracion()

        self.construir_interfaz()

    def construir_interfaz(self):
        # titulo
        titulo = tk.Label(self.root, text="S U D O K U",
                          bg="red", fg="white",
                          font=("Arial", 20, "bold"), pady=5)
        titulo.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # tablero
        self.frame_tablero = tk.Frame(self.root, bg="black")
        self.frame_tablero.grid(row=1, column=0, padx=10, pady=5)
        self.botones_tablero = []
        self.construir_tablero()

        # panel derecho
        self.frame_derecho = tk.Frame(self.root)
        self.frame_derecho.grid(row=1, column=1, padx=10, pady=5, sticky="n")
        self.construir_panel_derecho()

        # botones
        self.frame_botones = tk.Frame(self.root)
        self.frame_botones.grid(row=2, column=0, columnspan=2, pady=10)
        self.construir_botones()

    def construir_tablero(self):
        for fila in range(9):
            fila_botones = []
            for col in range(9):
                grosor_top    = 3 if fila % 3 == 0 else 1
                grosor_left   = 3 if col % 3 == 0 else 1
                grosor_bottom = 3 if fila == 8 else 1
                grosor_right  = 3 if col == 8 else 1
                btn = tk.Button(self.frame_tablero, text="",
                                width=3, height=1,
                                font=("Arial", 14, "bold"),
                                relief="flat", bg="white",
                                command=lambda f=fila, c=col: self.click_casilla(f, c))
                btn.grid(row=fila, column=col,
                         padx=(grosor_left, grosor_right),
                         pady=(grosor_top, grosor_bottom))
                fila_botones.append(btn)
            self.botones_tablero.append(fila_botones)

    def construir_panel_derecho(self):
        # nombre jugador
        def validar_largo(texto):
            return len(texto) <= 30

        vcmd = (self.root.register(validar_largo), '%P')
        tk.Label(self.frame_derecho, text="JUGADOR").pack()
        self.entry_jugador = tk.Entry(self.frame_derecho, width=20,
                               validate='key', validatecommand=vcmd)
        self.entry_jugador.pack(pady=5)

        # panel de numeros
        frame_nums = tk.Frame(self.frame_derecho)
        frame_nums.pack(pady=10)
        self.botones_elementos = []
        elementos = self.config.get("elementos", "numeros")
        lista = NUMEROS if elementos == "numeros" else LETRAS
        for i, val in enumerate(lista):
            btn = tk.Button(frame_nums, text=val, width=3, height=1,
                            font=("Arial", 12),
                            command=lambda v=val: self.seleccionar_elemento(v))
            btn.grid(row=i//3, column=i%3, padx=3, pady=3)
            self.botones_elementos.append(btn)
        # etiqueta nivel
        self.label_nivel = tk.Label(self.frame_derecho, 
                             text="Nivel: " + self.config["nivel"])
        self.label_nivel.pack(pady=5)

        # cronometro
        frame_reloj = tk.Frame(self.frame_derecho)
        frame_reloj.pack(pady=5)
        tk.Label(frame_reloj, text="Cronometro").grid(row=0, columnspan=3)
        tk.Label(frame_reloj, text="Horas").grid(row=1, column=0)
        tk.Label(frame_reloj, text="Minutos").grid(row=1, column=1)
        tk.Label(frame_reloj, text="Segundos").grid(row=1, column=2)
        self.label_horas   = tk.Label(frame_reloj, text="00", width=4, relief="sunken")
        self.label_minutos = tk.Label(frame_reloj, text="00", width=4, relief="sunken")
        self.label_segs    = tk.Label(frame_reloj, text="00", width=4, relief="sunken")
        self.label_horas.grid(row=2, column=0, padx=3)
        self.label_minutos.grid(row=2, column=1, padx=3)
        self.label_segs.grid(row=2, column=2, padx=3)

    def construir_botones(self):
        botones = [
            ("INICIAR JUEGO",   "hotpink",  self.iniciar_juego),
            ("DESHACER JUGADA", "cyan",     self.deshacer_jugada),
            ("BORRAR JUEGO",    "lightblue",self.borrar_juego),
            ("TOP X",           "yellow",   self.ver_top),
            ("REHACER JUGADA",  "cyan",     self.rehacer_jugada),
            ("TERMINAR JUEGO",  "green",    self.terminar_juego),
            ("GUARDAR JUEGO",   "white",    self.guardar_juego),
            ("CARGAR JUEGO",    "white",    self.cargar_juego),
        ]
        for i, (texto, color, cmd) in enumerate(botones):
            btn = tk.Button(self.frame_botones, text=texto, bg=color,
                    font=("Arial", 10, "bold"), width=14,
                    command=cmd)
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)
            if texto == "INICIAR JUEGO":
                self.btn_iniciar = btn

    def click_casilla(self, fila, col): 
        if self.juego_iniciado == False:
            messagebox.showerror("ERROR", "EL JUEGO NO HA INICIADO")
            return 
        if self.elemento_seleccionado == None:
            messagebox.showerror("ERROR", "NO EXISTE UN ELEMENTO SELECCIONADO") 
            return 
        valido, mensaje = validar_jugada(self.tablero, self.fijas, fila, col, self.elemento_seleccionado)

        if not valido:
            messagebox.showerror("ERROR", mensaje)
            self.botones_tablero[fila][col].config(bg = "red")
            return 
         # jugada valida: poner el numero en el tablero
        self.tablero[fila][col] = self.elemento_seleccionado
        self.botones_tablero[fila][col].config(text=self.elemento_seleccionado, bg="white")
        pila_push(self.pila_realizadas, (fila, col, self.elemento_seleccionado))
        # verificar si el juego esta completo
        if juego_completo(self.tablero):
            messagebox.showinfo("FELICIDADES", "EXCELENTE! JUEGO COMPLETADO")
            self.juego_iniciado = False
            self.btn_iniciar.config(state="normal")


    def seleccionar_elemento(self, valor):
        self.elemento_seleccionado = valor 
        #recorrer botones del panel 
        for btn in self.botones_elementos:
            if btn["text"] == valor:
                btn.config(bg = "green") #marca el numero seleccionad
            else:
                btn.config(bg = "SystemButtonFace")
    def iniciar_juego(self):
        #verificar el nombre
        nombre = self.entry_jugador.get() 
        if len(nombre) < 1 or len(nombre) > 30:
            messagebox.showerror("Error", "El nombre del jugador debe tener entre 1 y 30 caracteres")
            return 
        #cargar partida aleatoria 
        partida = obtener_partida_aleatoria(self.config["nivel"]) 
        if partida is None:
            messagebox.showerror("ERROR", "NO HAY PARTIDAS DE ESTE NIVEL") 
            return 
        #llnear tablero 
        # si la casilla tiene un numero diferente de cero es una casilla fija
        for i in range(9):
            for j in range(9):
                valor = partida["tablero"][i][j]
                self.tablero[i][j] = valor
                if valor != 0: 
                    self.fijas[i][j] = True 
                    self.botones_tablero[i][j].config(text=str(valor), bg="lightgray")
                else:
                    self.fijas[i][j] = False
                    self.botones_tablero[i][j].config(text="", bg="white")
        self.pila_realizadas = crear_pila()
        self.pila_eliminadas = crear_pila()
        #marco el juego como iniciado
        self.juego_iniciado = True
        #deshabilitar boton de iniciar juego
        self.btn_iniciar.config(state = "disabled") 

    def deshacer_jugada(self):
        if not self.juego_iniciado:
            messagebox.showerror("ERROR:", "NO SE HA INICIADO EL JUEGO")
            return 
        if pila_vacia(self.pila_realizadas):
            messagebox.showerror("ERROR", "NO HAY JUGADAS PARA DESHACER")
            return
        fila, col, valor = pila_pop(self.pila_realizadas)
        self.tablero[fila][col] = 0
        self.botones_tablero[fila][col].config(text="", bg="white") 
        pila_push(self.pila_eliminadas,(fila,col,valor))

    def rehacer_jugada(self):
        if not self.juego_iniciado:
            messagebox.showerror("ERROR:", "NO SE HA INICIADO EL JUEGO")
            return 
        if pila_vacia(self.pila_eliminadas):
            messagebox.showerror("ERROR", "NO HAY JUGADAS PARA REHACER")
            return
        fila, col, valor = pila_pop(self.pila_eliminadas)
        self.tablero[fila][col] =  valor
        self.botones_tablero[fila][col].config(text=valor,bg="white")
        pila_push(self.pila_realizadas,(fila,col,valor))

    def borrar_juego(self): 
        if not self.juego_iniciado:
            messagebox.showerror("ERROR:","NO SE HA INICIADO EL JUEGO")
            return
        respuesta = messagebox.askyesno("BORRAR EL JUEGO", "ESTA SEGURO DE BORRAR EL JUEGO? SI/NO")
        if respuesta:
        # recorrer el tablero y borrar las casillas que no son fijas
            for i in range(9):
                for j in range(9):
                    if not self.fijas[i][j]:
                        self.tablero[i][j] = 0
                        self.botones_tablero[i][j].config(text="", bg="white")
        # reiniciar las pilas
            self.pila_realizadas = crear_pila()
            self.pila_eliminadas = crear_pila()
    def terminar_juego(self): pass
    def ver_top(self): pass
    def guardar_juego(self): pass
    def cargar_juego(self): pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop() 

