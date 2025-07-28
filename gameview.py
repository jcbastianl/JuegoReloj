# gameview.py - Vista del Juego Solitario Reloj

import tkinter as tk
from tkinter import messagebox
import math

# Constantes del juego
ANCHO_CARTA, ALTO_CARTA = 75, 110
ANCHO_CANVAS, ALTO_CANVAS = 800, 700
DESPLAZAMIENTO_MONTON_X = 3
DESPLAZAMIENTO_MONTON_Y = 3

class VistaJuego(tk.Frame):
    # Clase para manejar la interfaz gráfica del juego
    
    def __init__(self, ventana_padre, controlador, gestor_recursos):
        # Inicializar la vista del juego
        super().__init__(ventana_padre, bg="darkgreen")
        self.ventana_padre = ventana_padre
        self.controlador = controlador
        self.recursos = gestor_recursos
        self.posiciones_montones = self._calcular_posiciones()
        self.animacion_ejecutandose = False
        self.carta_revelada = None
        self.monton_revelado = None

        # Crear lienzo principal
        self.lienzo = tk.Canvas(self, bg="darkgreen", width=ANCHO_CANVAS, height=ALTO_CANVAS, highlightthickness=0)
        self.lienzo.pack(fill=tk.BOTH, expand=True)
        #ese es el llenado   
        # Crear etiquetas de texto
        self.etiqueta_estado = tk.Label(self, text="", bg="darkgreen", fg="white", font=("Arial", 14))
        self.etiqueta_carta_actual = tk.Label(self, text="", bg="darkgreen", fg="yellow", font=("Arial", 12, "bold"))
        
        # Posicionar etiquetas
        self.lienzo.create_window(ANCHO_CANVAS / 2, 20, window=self.etiqueta_estado)
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.etiqueta_carta_actual)

        # Detectar clics del usuario
        self.lienzo.bind("<Button-1>", self.al_hacer_clic_lienzo)

    def al_hacer_clic_lienzo(self, evento):
        # Manejar clics en el lienzo
        if self.animacion_ejecutandose: 
            return
            
        indice_monton = self._identificar_monton(evento.x, evento.y)
        if indice_monton:
            self.controlador.manejar_clic_monton(indice_monton)

    def dibujar_tablero(self, estado_tablero):
        # Dibujar todo el tablero del juego
        self.lienzo.delete("monton", "botones_juego", "revelado", "botones_menu")
        
        montones_visibles = estado_tablero['visible']
        conteos_ocultos = estado_tablero['conteos_ocultos']
        carta_actual = estado_tablero.get('carta_actual')
        revelacion_pendiente = estado_tablero.get('revelacion_pendiente')

        # Botón de menú
        boton_menu = tk.Button(self, text="🏠 Menú Principal", 
                              command=self.controlador.terminar_juego_actual, 
                              bg="#4ECDC4", fg="black", font=("Arial", 9))
        self.lienzo.create_window(ANCHO_CANVAS - 80, 40, window=boton_menu, tags="botones_juego")

        # Dibujar los 13 montones
        for i in range(1, 14):
            x, y = self.posiciones_montones[i]
            
            # Resaltar montones según el estado
            if revelacion_pendiente == i:
                self.lienzo.create_rectangle(x - 8, y - 8, x + ANCHO_CARTA + 8, y + ALTO_CARTA + 8, 
                                           fill="", outline="lime", width=5, tags="monton")
            elif carta_actual and self.obtener_destino_carta(carta_actual) == i:
                self.lienzo.create_rectangle(x - 6, y - 6, x + ANCHO_CARTA + 6, y + ALTO_CARTA + 6, 
                                           fill="", outline="orange", width=3, tags="monton")

            # Dibujar cartas ocultas
            if conteos_ocultos.get(i, 0) > 0:
                for j in range(min(conteos_ocultos[i], 5)):
                     self.lienzo.create_image(x - j * DESPLAZAMIENTO_MONTON_X, 
                                            y - j * DESPLAZAMIENTO_MONTON_Y, 
                                            image=self.recursos.obtener_imagen('back'), 
                                            anchor='nw', tags="monton")
                if conteos_ocultos[i] > 1:
                    self.lienzo.create_text(x + ANCHO_CARTA - 10, y + 10, 
                                          text=str(conteos_ocultos[i]), 
                                          fill="yellow", font=("Arial", 10, "bold"), tags="monton")

            # Dibujar carta visible
            nombre_carta = montones_visibles.get(i, 'back')
            if nombre_carta != 'back':
                imagen = self.recursos.obtener_imagen(nombre_carta)
                if imagen: 
                    self.lienzo.create_image(x, y, image=imagen, anchor='nw', tags="monton")
            elif conteos_ocultos.get(i, 0) == 0:
                self.lienzo.create_rectangle(x, y, x + ANCHO_CARTA, y + ALTO_CARTA, 
                                           fill="darkgreen", outline="gray", dash=(5, 5), tags="monton")
            
            # Número del montón
            self.lienzo.create_text(x + ANCHO_CARTA / 2, y - 15, text=str(i), 
                                  fill="white", font=("Arial", 12, "bold"), tags="monton")

        # Mostrar carta revelada si existe
        if self.carta_revelada and self.monton_revelado: 
            self.dibujar_carta_revelada()
            
        self.actualizar_etiquetas_estado(carta_actual)

    def dibujar_carta_revelada(self):
        # Dibujar efectos especiales para carta revelada
        x_monton, y_monton = self.posiciones_montones[self.monton_revelado]
        desplazamiento_x, desplazamiento_y = -15, -15
        
        # Borde amarillo alrededor del montón
        self.lienzo.create_rectangle(x_monton - 5, y_monton - 5, 
                                   x_monton + ANCHO_CARTA + 5, y_monton + ALTO_CARTA + 5, 
                                   fill="", outline="yellow", width=4, tags="revelado")
        
        # Carta revelada con desplazamiento
        imagen = self.recursos.obtener_imagen(self.carta_revelada)
        if imagen: 
            self.lienzo.create_image(x_monton + desplazamiento_x, y_monton + desplazamiento_y, 
                                   image=imagen, anchor='nw', tags="revelado")
        
        # Texto indicando destino
        destino = self.obtener_destino_carta(self.carta_revelada)
        self.lienzo.create_text(x_monton + desplazamiento_x + ANCHO_CARTA/2, 
                              y_monton + desplazamiento_y + ALTO_CARTA + 15, 
                              text=f"→ Montón {destino}", fill="white", font=("Arial", 10, "bold"), tags="revelado")

    def mostrar_carta_revelada(self, carta, monton):
        # Establecer carta revelada y redibujar
        self.carta_revelada, self.monton_revelado = carta, monton
        self.dibujar_tablero(self.controlador.modelo.obtener_estado_tablero())

    def ocultar_carta_revelada(self):
        # Quitar efectos de carta revelada
        self.carta_revelada, self.monton_revelado = None, None

    def animar_movimiento_carta(self, carta, monton_origen, monton_destino, funcion_callback=None):
        # Animar movimiento de carta entre montones
        if self.animacion_ejecutandose:
            if funcion_callback: 
                funcion_callback()
            return
            
        self.animacion_ejecutandose = True
        
        x_origen, y_origen = self.posiciones_montones.get(monton_origen, (0,0))
        x_destino, y_destino = self.posiciones_montones.get(monton_destino, (0,0))
        
        imagen = self.recursos.obtener_imagen(carta)
        if imagen:
            carta_animada = self.lienzo.create_image(x_origen, y_origen, image=imagen, anchor='nw')
            
            pasos = 20
            delta_x, delta_y = (x_destino - x_origen) / pasos, (y_destino - y_origen) / pasos
            
            def paso_movimiento(paso):
                if paso < pasos:
                    self.lienzo.move(carta_animada, delta_x, delta_y)
                    self.ventana_padre.after(20, lambda: paso_movimiento(paso + 1))
                else:
                    self.lienzo.delete(carta_animada)
                    self.animacion_ejecutandose = False
                    if funcion_callback: 
                        funcion_callback()
            
            paso_movimiento(0)
        else:
            self.animacion_ejecutandose = False
            if funcion_callback: 
                funcion_callback()

    def animar_barajado(self, funcion_callback=None):
        # Animación visual de barajado
        if self.animacion_ejecutandose:
            if funcion_callback: 
                funcion_callback()
            return
            
        self.animacion_ejecutandose = True
        
        # Limpiar lienzo pero mantener etiquetas
        self.lienzo.delete("all")
        self.lienzo.create_window(ANCHO_CANVAS / 2, 20, window=self.etiqueta_estado)
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.etiqueta_carta_actual)
        
        # Crear cartas que giran en círculo
        centro_x, centro_y = ANCHO_CANVAS / 2, ALTO_CANVAS / 2
        cartas = []
        
        for i in range(8):
            imagen_carta = self.lienzo.create_image(
                centro_x + i * 2, centro_y + i * 2, 
                image=self.recursos.obtener_imagen('back'), 
                anchor='center', tags="animacion_barajado"
            )
            cartas.append(imagen_carta)
        
        paso = 0
        def paso_animacion():
            nonlocal paso
            if paso > 40:
                self.lienzo.delete("animacion_barajado")
                self.animacion_ejecutandose = False
                
                if funcion_callback:
                    try:
                        funcion_callback()
                    except Exception as error:
                        print(f"Error en el callback del barajado: {error}")
                        self.controlador.mostrar_menu_principal()
                return
            
            # Mover cartas en círculo
            for i, carta in enumerate(cartas):
                angulo = math.radians(paso * 9 + i * 45)
                desplazamiento_x = 80 * math.cos(angulo)
                desplazamiento_y = 80 * math.sin(angulo)
                self.lienzo.coords(carta, centro_x + desplazamiento_x, centro_y + desplazamiento_y)
            
            paso += 1
            self.ventana_padre.after(30, paso_animacion)
        
        paso_animacion()

    def obtener_destino_carta(self, carta):
        # Calcular a qué montón debe ir una carta
        if not carta: 
            return None
            
        valor = carta[:-1]  # Valor sin el palo
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        try: 
            return valores.index(valor) + 1
        except ValueError: 
            return 13  # Por defecto al centro

    def mostrar_mensaje_estado(self, mensaje):
        # Mostrar mensaje en la parte superior
        self.etiqueta_estado.config(text=mensaje)

    def actualizar_etiquetas_estado(self, carta_actual):
        # Actualizar información de carta actual
        if carta_actual:
            destino = self.obtener_destino_carta(carta_actual)
            self.etiqueta_carta_actual.config(text=f"Carta Actual: {carta_actual} → Montón {destino}")
        else:
            self.etiqueta_carta_actual.config(text="No hay carta actual")

    def mostrar_mensaje_fin_juego(self, titulo, mensaje):
        # Mostrar mensaje cuando termina el juego
        messagebox.showinfo(titulo, mensaje)
        self.controlador.mostrar_menu_principal()

    def mostrar_menu(self):
        # Mostrar menú principal con botones
        self.lienzo.delete("all")
        
        self.etiqueta_estado.config(text="🎴 Solitario Reloj 🎴")
        self.etiqueta_carta_actual.config(text="Selecciona un modo de juego para comenzar")
        
        self.lienzo.create_window(ANCHO_CANVAS / 2, 40, window=self.etiqueta_estado)
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.etiqueta_carta_actual)

        # Crear botones del menú
        boton_automatico = tk.Button(self, text="🤖 Modo Automático", 
                                   command=lambda: self.controlador.iniciar_juego_nuevo('auto'), 
                                   font=("Arial", 12), width=20, height=2)
        boton_manual = tk.Button(self, text="🎮 Modo Manual", 
                               command=lambda: self.controlador.iniciar_juego_nuevo('manual'), 
                               font=("Arial", 12), width=20, height=2)
        boton_barajar = tk.Button(self, text="🎲 Barajar y Reiniciar", 
                                command=self.controlador.barajar_cartas, 
                                font=("Arial", 12), width=20, height=2)
        boton_salir = tk.Button(self, text="❌ Salir del Juego", 
                              command=self.controlador.salir_juego, 
                              font=("Arial", 12), width=20, height=2)
        
        # Posicionar botones
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 - 100, window=boton_automatico, tags="botones_menu")
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 - 30, window=boton_manual, tags="botones_menu")
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 + 40, window=boton_barajar, tags="botones_menu")
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 + 110, window=boton_salir, tags="botones_menu")

    def _calcular_posiciones(self):
        # Calcular posiciones de montones en forma de reloj
        posiciones = {}
        centro_x, centro_y, radio = ANCHO_CANVAS / 2, ALTO_CANVAS / 2, 250
        
        # Montones 1-12 en círculo como reloj
        for i in range(1, 13):
            angulo = math.radians(-60 + (i * 30))  # -60°  
            x = centro_x + radio * math.cos(angulo) - (ANCHO_CARTA / 2)
            y = centro_y + radio * math.sin(angulo) - (ALTO_CARTA / 2)
            posiciones[i] = (x, y)
        
        # Montón 13 en el centro
        posiciones[13] = (centro_x - ANCHO_CARTA / 2, centro_y - ALTO_CARTA / 2)
        return posiciones

    def _identificar_monton(self, x, y):
        # Identificar en qué montón hizo clic el usuario
        for i, (pos_x, pos_y) in self.posiciones_montones.items():
            if pos_x <= x <= pos_x + ANCHO_CARTA and pos_y <= y <= pos_y + ALTO_CARTA:
                return i
        return None