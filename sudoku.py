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
    # Retorna una matriz 9x9 inicializada en cero
    tablero = []
    for i in range(9):
        fila = []
        for j in range(9):
            fila.append(0)
        tablero.append(fila)
    return tablero

def crear_matriz_fijas():
    # Retorna una matriz 9x9 de False (ninguna casilla es fija)
    matriz = []
    for i in range(9):
        fila = []
        for j in range(9):
            fila.append(False)
        matriz.append(fila)
    return matriz

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
        config = json.load(f)

    # migrar formato viejo: "reloj" era string, ahora es dict anidado
    if type(config.get("reloj")) != dict:
        tipo_viejo = config.get("reloj", "cronometro")
        horas_viejas = 0
        minutos_viejos = 0
        segundos_viejos = 0
        if "timer_horas" in config:
            horas_viejas = config["timer_horas"]
            del config["timer_horas"]
        if "timer_minutos" in config:
            minutos_viejos = config["timer_minutos"]
            del config["timer_minutos"]
        if "timer_segundos" in config:
            segundos_viejos = config["timer_segundos"]
            del config["timer_segundos"]
        config["reloj"] = {
            "tipo":     tipo_viejo,
            "horas":    horas_viejas,
            "minutos":  minutos_viejos,
            "segundos": segundos_viejos
        }
    # migrar llave "top_x" -> "top x"
    if "top_x" in config:
        if "top x" not in config:
            config["top x"] = config["top_x"]
        del config["top_x"]

    # guardar el archivo ya en el formato nuevo
    with open(ARCHIVO_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

    return config

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

def guardar_en_bitacora(jugador, nivel, segundos, fecha_hora):
    # Guarda una partida completada en la bitacora
    bitacora = {}
    if os.path.exists(ARCHIVO_BITACORA):
        with open(ARCHIVO_BITACORA, 'r', encoding='utf-8') as f:
            bitacora = json.load(f)
    entrada = {
        "dificultad": nivel,
        "tiempo": segundos,
        "fecha_hora": fecha_hora
    }
    if jugador not in bitacora:
        bitacora[jugador] = []
    bitacora[jugador].append(entrada)
    with open(ARCHIVO_BITACORA, 'w', encoding='utf-8') as f:
        json.dump(bitacora, f, indent=4)



class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SUDOKU - TEC")
        self.root.resizable(False, False)
        self.juego_cargado = False
        # variables del juego
        self.tablero        = crear_tablero_vacio()
        self.fijas          = crear_matriz_fijas()
        self.tablero_orig   = crear_tablero_vacio()
        self.pila_realizadas  = crear_pila()
        self.pila_eliminadas  = crear_pila()
        self.juego_iniciado = False
        self.elemento_seleccionado = None
        self.config = cargar_configuracion()
        self.segundos_totales = 0
        self.segundos_jugados = 0
        self.cronometro_activo = False

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
        tk.Label(self.frame_derecho, text="JUGADOR").pack()
        self.entry_jugador = tk.Entry(self.frame_derecho, width=20)
        self.entry_jugador.pack(pady=5)

        # panel de numeros
        frame_nums = tk.Frame(self.frame_derecho)
        frame_nums.pack(pady=10)
        self.botones_elementos = []
        elementos = self.config.get("elementos", "numeros")
        if elementos == "numeros":
            lista = NUMEROS
        else:
            lista = LETRAS
        fila_btn = 0
        col_btn = 0
        for val in lista:
            btn = tk.Button(frame_nums, text=val, width=3, height=1,
                            font=("Arial", 12),
                            command=lambda v=val: self.seleccionar_elemento(v))
            btn.grid(row=fila_btn, column=col_btn, padx=3, pady=3)
            self.botones_elementos.append(btn)
            col_btn += 1
            if col_btn == 3:
                col_btn = 0
                fila_btn += 1
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
        fila_btn = 0
        col_btn = 0
        for i in range(len(botones)):
            texto = botones[i][0]
            color = botones[i][1]
            cmd   = botones[i][2]
            btn = tk.Button(self.frame_botones, text=texto, bg=color,
                    font=("Arial", 10, "bold"), width=14,
                    command=cmd)
            btn.grid(row=fila_btn, column=col_btn, padx=5, pady=5)
            if texto == "INICIAR JUEGO":
                self.btn_iniciar = btn
            col_btn += 1
            if col_btn == 4:
                col_btn = 0
                fila_btn += 1

        menu_botones = [
            ("CONFIGURAR", "orange",     self.abrir_configuracion),
            ("AYUDA",      "lightgreen", self.abrir_ayuda),
            ("ACERCA DE",  "lightblue",  self.abrir_acerca),
            ("SALIR",      "red",        self.root.quit),
        ]
        for i in range(len(menu_botones)):
            texto = menu_botones[i][0]
            color = menu_botones[i][1]
            cmd   = menu_botones[i][2]
            tk.Button(self.frame_botones, text=texto, bg=color,
                      font=("Arial", 10, "bold"), width=14,
                      command=cmd).grid(row=2, column=i, padx=5, pady=5)

    def click_casilla(self, fila, col): 
        if self.juego_iniciado == False:
            messagebox.showerror("ERROR", "EL JUEGO NO HA INICIADO")
            return 
        if self.elemento_seleccionado == None:
            messagebox.showerror("ERROR", "FALTA SELECCIONAR UN ELEMENTO")
            return
        elementos = self.config.get("elementos", "numeros")
        if elementos == "numeros":
            valor_int = int(self.elemento_seleccionado)
        else:
            valor_int = LETRAS.index(self.elemento_seleccionado) + 1
        valido, mensaje = validar_jugada(self.tablero, self.fijas, fila, col, valor_int)
        if not valido:
            self.botones_tablero[fila][col].config(bg="red")
            messagebox.showerror("ERROR", mensaje)
            if self.fijas[fila][col]:
                orig_bg = "lightgray"
            else:
                orig_bg = "white"
            self.botones_tablero[fila][col].config(bg=orig_bg)
            return
        # jugada valida: poner el numero en el tablero
        self.tablero[fila][col] = valor_int
        self.botones_tablero[fila][col].config(text=self.elemento_seleccionado, bg="white")
        pila_push(self.pila_realizadas, (fila, col, valor_int))
        self.pila_eliminadas = crear_pila()
        # verificar si el juego esta completo
        if juego_completo(self.tablero):
            self.cronometro_activo = False
            nombre = self.entry_jugador.get()
            nivel = self.config["nivel"]
            fecha_hora = datetime.now().strftime("%Y%m%dT%H%M%S")
            if self.config["reloj"]["tipo"] != "ninguno":
                guardar_en_bitacora(nombre, nivel, self.segundos_jugados, fecha_hora)
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


    def actualizar_cronometro(self):
        if self.cronometro_activo:
            tipo = self.config["reloj"]["tipo"]
            self.segundos_jugados += 1
            if tipo == "timer":
                self.segundos_totales -= 1
                if self.segundos_totales <= 0:
                    self.segundos_totales = 0
                    self.label_horas.config(text="00")
                    self.label_minutos.config(text="00")
                    self.label_segs.config(text="00")
                    self.cronometro_activo = False
                    self.juego_iniciado = False
                    self.btn_iniciar.config(state="normal")
                    messagebox.showwarning("TIEMPO", "TIEMPO EXPIRADO. JUEGO TERMINADO.")
                    return
            else:
                self.segundos_totales += 1
            horas   = self.segundos_totales // 3600
            minutos = (self.segundos_totales % 3600) // 60
            segs    = self.segundos_totales % 60
            self.label_horas.config(text=str(horas).zfill(2))
            self.label_minutos.config(text=str(minutos).zfill(2))
            self.label_segs.config(text=str(segs).zfill(2))
            self.root.after(1000, self.actualizar_cronometro)

            
    def iniciar_juego(self):
        # verificar el nombre
        nombre = self.entry_jugador.get()
        if len(nombre) < 1 or len(nombre) > 30:
            messagebox.showerror("Error", "El nombre del jugador debe tener entre 1 y 30 caracteres")
            return
        # si no hay juego cargado, cargar partida nueva
        if not self.juego_cargado:
            partida = obtener_partida_aleatoria(self.config["nivel"])
            if partida is None:
                messagebox.showerror("ERROR", "NO HAY PARTIDAS DE ESTE NIVEL")
                return
            for i in range(9):
                for j in range(9):
                    valor = partida["tablero"][i][j]
                    self.tablero[i][j] = valor
                    if valor != 0:
                        self.fijas[i][j] = True
                        elementos_cfg = self.config.get("elementos", "numeros")
                        if elementos_cfg == "numeros":
                            texto_fija = str(valor)
                        else:
                            texto_fija = LETRAS[valor - 1]
                        self.botones_tablero[i][j].config(text=texto_fija, bg="lightgray")
                    else:
                        self.fijas[i][j] = False
                        self.botones_tablero[i][j].config(text="", bg="white")
        # reiniciar pilas y estado
        self.pila_realizadas = crear_pila()
        self.pila_eliminadas = crear_pila()
        self.juego_cargado = False
        self.juego_iniciado = True
        self.btn_iniciar.config(state="disabled")
        # arrancar reloj segun tipo configurado
        tipo_reloj = self.config["reloj"]["tipo"]
        self.segundos_jugados = 0
        if tipo_reloj == "timer":
            h = self.config["reloj"]["horas"]
            m = self.config["reloj"]["minutos"]
            s = self.config["reloj"]["segundos"]
            self.segundos_totales = h * 3600 + m * 60 + s
            self.cronometro_activo = True
            self.actualizar_cronometro()
        elif tipo_reloj == "cronometro":
            self.segundos_totales = 0
            self.cronometro_activo = True
            self.actualizar_cronometro()
        else:
            self.segundos_totales = 0
            self.cronometro_activo = False
            self.label_horas.config(text="--")
            self.label_minutos.config(text="--")
            self.label_segs.config(text="--")

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
        self.tablero[fila][col] = valor
        elementos = self.config.get("elementos", "numeros")
        if elementos == "numeros":
            texto_mostrar = str(valor)
        else:
            texto_mostrar = LETRAS[valor - 1]
        self.botones_tablero[fila][col].config(text=texto_mostrar, bg="white")
        pila_push(self.pila_realizadas, (fila, col, valor))

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
    def terminar_juego(self): 
        if not self.juego_iniciado:
            messagebox.showerror("ERROR:", "EL JUEGO NO HA SIDO INICIADO")
            return
        respuesta = messagebox.askyesno("ELIMINAR JUEGO", "ESTA SEGURO DE TERMINAR EL JUEGO? SI/NO")
        if respuesta:
            self.tablero = crear_tablero_vacio()
            self.fijas = crear_matriz_fijas() 
            for i in range(9):
                for j in range (9):
                    self.botones_tablero[i][j].config(text = "", bg = "white")
            #se reinician las pilas
            self.cronometro_activo = False
            self.pila_realizadas = crear_pila()
            self.pila_eliminadas = crear_pila()
            self.juego_iniciado = False
            self.elemento_seleccionado = None
            self.btn_iniciar.config(state="normal")

    def ver_top(self):
        # detener reloj mientras se ve el top
        estaba_activo = self.cronometro_activo
        self.cronometro_activo = False

        if not os.path.exists(ARCHIVO_BITACORA):
            messagebox.showinfo("TOP", "No hay partidas registradas aun")
            self.cronometro_activo = estaba_activo
            if estaba_activo:
                self.actualizar_cronometro()
            return

        with open(ARCHIVO_BITACORA, 'r', encoding='utf-8') as f:
            bitacora = json.load(f)

        top_x = self.config["top x"]

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas as pdf_canvas
        except ImportError:
            messagebox.showerror("ERROR",
                "Falta la libreria reportlab.\nInstalala con: pip install reportlab")
            self.cronometro_activo = estaba_activo
            if estaba_activo:
                self.actualizar_cronometro()
            return

        pdf_path = "sudoku2026_top.pdf"
        _, alto = letter
        c = pdf_canvas.Canvas(pdf_path, pagesize=letter)
        y = alto - 50

        if top_x > 0:
            titulo = "TOP " + str(top_x)
        else:
            titulo = "TOP TODOS"
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, titulo)
        y -= 30

        for nivel in ["dificil", "intermedio", "facil"]:
            # recopilar partidas de este nivel desde todos los jugadores
            entradas = []
            for jugador in bitacora:
                for partida in bitacora[jugador]:
                    if partida["dificultad"] == nivel:
                        entradas.append((partida["tiempo"], jugador, partida["fecha_hora"]))

            # ordenar por tiempo de menor a mayor (burbuja simple)
            for i in range(len(entradas)):
                for j in range(i + 1, len(entradas)):
                    if entradas[i][0] > entradas[j][0]:
                        temp = entradas[i]
                        entradas[i] = entradas[j]
                        entradas[j] = temp

            if top_x > 0:
                entradas = entradas[:top_x]

            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "NIVEL " + nivel.upper() + ":")
            y -= 18
            c.setFont("Helvetica", 10)

            if not entradas:
                c.drawString(70, y, "Sin partidas registradas")
                y -= 14
            else:
                for i in range(len(entradas)):
                    tiempo, jugador, fecha_hora = entradas[i]
                    hh = tiempo // 3600
                    mm = (tiempo % 3600) // 60
                    ss = tiempo % 60
                    tiempo_str = str(hh) + ":" + str(mm).zfill(2) + ":" + str(ss).zfill(2)
                    try:
                        dt = datetime.strptime(fecha_hora, "%Y%m%dT%H%M%S")
                        fecha_str = dt.strftime("%d-%m-%Y %H:%M:%S")
                    except ValueError:
                        fecha_str = fecha_hora
                    linea = str(i + 1) + "-  " + jugador + "    " + tiempo_str + "    " + fecha_str
                    c.drawString(70, y, linea)
                    y -= 14
                    if y < 60:
                        c.showPage()
                        y = alto - 50

            y -= 10

        c.save()
        os.startfile(pdf_path)
        messagebox.showinfo("TOP", "Presione OK para continuar el juego")

        # reanudar el reloj
        self.cronometro_activo = estaba_activo
        if estaba_activo:
            self.actualizar_cronometro()

    def abrir_configuracion(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Configuracion")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.focus_force()
        ventana.columnconfigure(0, minsize=130)
        ventana.columnconfigure(1, minsize=130)
        ventana.columnconfigure(2, minsize=130)

        tk.Label(ventana, text="Nivel:", font=("Arial", 11, "bold")).grid(
            row=0, column=0, padx=10, pady=5, sticky="w")
        nivel_var = tk.StringVar(value=self.config["nivel"])
        for i in range(len(NIVELES)):
            tk.Radiobutton(ventana, text=NIVELES[i].capitalize(), variable=nivel_var,
                           value=NIVELES[i]).grid(row=i+1, column=0, padx=20, sticky="w")

        tk.Label(ventana, text="Reloj:", font=("Arial", 11, "bold")).grid(
            row=0, column=1, padx=10, pady=5, sticky="w")
        reloj_var = tk.StringVar(value=self.config["reloj"]["tipo"])
        reloj_opciones = [("cronometro", "Cronometro"), ("timer", "Timer"), ("ninguno", "Ninguno")]
        for i in range(len(reloj_opciones)):
            valor   = reloj_opciones[i][0]
            etiqueta = reloj_opciones[i][1]
            tk.Radiobutton(ventana, text=etiqueta, variable=reloj_var,
                           value=valor).grid(row=i+1, column=1, padx=20, sticky="w")

        # Campos de tiempo para el timer (horas 0-4, minutos 0-59, segundos 0-59)
        frame_timer = tk.Frame(ventana)
        frame_timer.grid(row=4, column=1, padx=20, pady=2, sticky="w")
        tk.Label(frame_timer, text="H").grid(row=0, column=0, padx=2)
        tk.Label(frame_timer, text="M").grid(row=0, column=1, padx=2)
        tk.Label(frame_timer, text="S").grid(row=0, column=2, padx=2)
        timer_h = tk.IntVar(value=self.config["reloj"]["horas"])
        timer_m = tk.IntVar(value=self.config["reloj"]["minutos"])
        timer_s = tk.IntVar(value=self.config["reloj"]["segundos"])
        tk.Spinbox(frame_timer, from_=0, to=4,  textvariable=timer_h, width=4).grid(row=1, column=0, padx=2)
        tk.Spinbox(frame_timer, from_=0, to=59, textvariable=timer_m, width=4).grid(row=1, column=1, padx=2)
        tk.Spinbox(frame_timer, from_=0, to=59, textvariable=timer_s, width=4).grid(row=1, column=2, padx=2)

        # los campos del timer siempre son visibles; solo se validan al guardar

        
        tk.Label(ventana, text="Elementos:", font=("Arial", 11, "bold")).grid(
            row=0, column=2, padx=10, pady=5, sticky="w")
        elem_var = tk.StringVar(value=self.config["elementos"])
        tk.Radiobutton(ventana, text="numeros", variable=elem_var,
                       value="numeros").grid(row=1, column=2, padx=20, sticky="w")
        tk.Radiobutton(ventana, text="letras", variable=elem_var,
                       value="letras").grid(row=2, column=2, padx=20, sticky="w")

        
        tk.Label(ventana, text="Top X (0=todos):", font=("Arial", 11, "bold")).grid(
            row=5, column=0, padx=10, pady=5, sticky="w")
        topx_var = tk.IntVar(value=self.config["top x"])
        tk.Spinbox(ventana, from_=0, to=10, textvariable=topx_var, width=5).grid(
            row=5, column=1, sticky="w")

        def guardar():
            # validar timer si fue seleccionado
            if reloj_var.get() == "timer":
                h = timer_h.get()
                m = timer_m.get()
                s = timer_s.get()
                if h == 0 and m == 0 and s == 0:
                    messagebox.showerror("ERROR",
                        "El timer debe tener al menos un valor mayor a cero")
                    return
            self.config["nivel"]          = nivel_var.get()
            self.config["reloj"]["tipo"]  = reloj_var.get()
            self.config["reloj"]["horas"] = timer_h.get()
            self.config["reloj"]["minutos"] = timer_m.get()
            self.config["reloj"]["segundos"] = timer_s.get()
            self.config["elementos"]      = elem_var.get()
            self.config["top x"]          = topx_var.get()
            with open(ARCHIVO_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            self.label_nivel.config(text="Nivel: " + self.config["nivel"])
            messagebox.showinfo("GUARDADO", "Configuracion guardada exitosamente")
            ventana.destroy()

        tk.Button(ventana, text="GUARDAR", bg="green", fg="white",
                  font=("Arial", 11, "bold"), command=guardar).grid(
                  row=6, column=0, columnspan=3, pady=10)
       
    def abrir_ayuda(self):
        # abre el manual de usuario en PDF si existe
        manual = "manual_de_usuario_sudoku.pdf"
        if os.path.exists(manual):
            os.startfile(manual)
        else:
            messagebox.showinfo("Ayuda", "El manual de usuario no esta disponible todavia.")
    def abrir_acerca(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Acerca de")
        ventana.geometry("300x200")
        ventana.grab_set()
        texto = ("Nombre: SUDOKU TEC\n"
             "Version: 1.0\n"
             "Fecha: Mayo 2026\n"
             "Autor: Aldrickson Yesua\n"
             "Curso: Taller de Programacion\n"
             "TEC - Cartago, Costa Rica")
        tk.Label(ventana, text=texto, justify="center",
             font=("Arial", 11), padx=10, pady=20).pack() 
        

    def guardar_juego(self):
        if not self.juego_iniciado:
            messagebox.showerror("ERROR:", "EL JUEGO NO HA SIDO INICIADO")
            return
        nombre = self.entry_jugador.get()
        nivel = self.config["nivel"]
        datos = {"jugador":nombre,"nivel":nivel,"tablero":self.tablero,"fijas":self.fijas}
        if os.path.exists(ARCHIVO_GUARDADO):
            with open(ARCHIVO_GUARDADO, 'r', encoding='utf-8') as f:
                guardado = json.load(f)
        else:
            guardado = {}

        clave = nombre + "_" + nivel
        guardado[clave] = datos

        with open(ARCHIVO_GUARDADO, 'w', encoding='utf-8') as f:
            json.dump(guardado, f, indent=4)
    
        messagebox.showinfo("GUARDADO", "JUEGO GUARDADO EXITOSAMENTE")
    def cargar_juego(self):
        
        if self.juego_iniciado:
            messagebox.showerror("ERROR:", "YA HAY UN JUEGO INICIADO")
            return
        nombre = self.entry_jugador.get() 
        if len(nombre) < 1 or len(nombre) > 30:
            messagebox.showerror("Error", "El nombre del jugador debe tener entre 1 y 30 caracteres")
            return 
        nivel = self.config["nivel"]
        clave = nombre + "_" + nivel
        
        if not os.path.exists(ARCHIVO_GUARDADO):
            messagebox.showerror("ERROR", "NO TIENE UN JUEGO GUARDADO CON ESTA DIFICULTAD")
            return
        
        with open(ARCHIVO_GUARDADO, 'r', encoding='utf-8') as f:
            guardado = json.load(f)

        if clave not in guardado:
            messagebox.showerror("ERROR", "NO TIENE UN JUEGO GUARDADO CON ESTA DIFICULTAD")
            return
        self.juego_cargado = True
        # cargar los datos guardados
        datos = guardado[clave]
        self.tablero = datos["tablero"]
        self.fijas   = datos["fijas"]

        # mostrar en pantalla
        elementos_cfg = self.config.get("elementos", "numeros")
        for i in range(9):
            for j in range(9):
                valor = self.tablero[i][j]
                if elementos_cfg == "numeros":
                    texto_val = str(valor)
                else:
                    texto_val = LETRAS[valor - 1] if valor != 0 else ""
                if self.fijas[i][j]:
                    self.botones_tablero[i][j].config(text=texto_val, bg="lightgray")
                elif valor != 0:
                    self.botones_tablero[i][j].config(text=texto_val, bg="white")
                else:
                    self.botones_tablero[i][j].config(text="", bg="white")
        
        messagebox.showinfo("CARGADO", "JUEGO CARGADO EXITOSAMENTE. PRESIONE INICIAR JUEGO PARA CONTINUAR")
if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop() 

