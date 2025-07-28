# gameview.py - Vista del Juego Solitario Reloj
# Este archivo maneja toda la interfaz gráfica y las animaciones del juego

import tkinter as tk
from tkinter import messagebox
import math

# Constantes para el diseño del juego
ANCHO_CARTA, ALTO_CARTA = 75, 110      # Tamaño de cada carta en píxeles
ANCHO_CANVAS, ALTO_CANVAS = 800, 700   # Tamaño de la ventana de juego
DESPLAZAMIENTO_MONTON_X = 3             # Desplazamiento horizontal entre cartas apiladas
DESPLAZAMIENTO_MONTON_Y = 3             # Desplazamiento vertical entre cartas apiladas

class VistaJuego(tk.Frame):
    """
    Clase que maneja toda la interfaz gráfica del juego.
    Se encarga de dibujar las cartas, botones, animaciones y responder a clics del usuario.
    """
    
    def __init__(self, ventana_padre, controlador, gestor_recursos):
        """
        Inicializa la vista del juego.
        
        Args:
            ventana_padre: La ventana principal de la aplicación
            controlador: El controlador que maneja la lógica del juego
            gestor_recursos: El gestor que carga las imágenes de las cartas
        """
        super().__init__(ventana_padre, bg="darkgreen")  # Fondo verde como mesa de cartas
        self.ventana_padre = ventana_padre
        self.controlador = controlador
        self.recursos = gestor_recursos
        self.posiciones_montones = self._calcular_posiciones()  # Calcula dónde van las cartas en el reloj
        self.animacion_ejecutandose = False                     # Controla si hay una animación en curso
        self.carta_revelada = None                              # Carta que se acaba de revelar
        self.monton_revelado = None                             # En qué montón se reveló la carta

        # Crear el lienzo donde se dibuja todo el juego
        self.lienzo = tk.Canvas(self, bg="darkgreen", width=ANCHO_CANVAS, height=ALTO_CANVAS, highlightthickness=0)
        self.lienzo.pack(fill=tk.BOTH, expand=True)

        # Crear las etiquetas de texto que muestran información
        self.etiqueta_estado = tk.Label(self, text="", bg="darkgreen", fg="white", font=("Arial", 14))
        self.etiqueta_carta_actual = tk.Label(self, text="", bg="darkgreen", fg="yellow", font=("Arial", 12, "bold"))
        
        # Posicionar las etiquetas en el lienzo
        self.lienzo.create_window(ANCHO_CANVAS / 2, 20, window=self.etiqueta_estado)
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.etiqueta_carta_actual)

        # Detectar cuando el usuario hace clic en el lienzo
        self.lienzo.bind("<Button-1>", self.al_hacer_clic_lienzo)

    def al_hacer_clic_lienzo(self, evento):
        """
        Se ejecuta cuando el usuario hace clic en algún lugar del lienzo.
        Identifica en qué montón hizo clic y se lo comunica al controlador.
        """
        # Si hay una animación ejecutándose, ignorar el clic
        if self.animacion_ejecutandose: 
            return
            
        # Identificar en qué montón hizo clic el usuario
        indice_monton = self._identificar_monton(evento.x, evento.y)
        if indice_monton:
            # Comunicar al controlador que se hizo clic en este montón
            self.controlador.manejar_clic_monton(indice_monton)

    def dibujar_tablero(self, estado_tablero):
        """
        Dibuja todo el tablero del juego: cartas, montones, botones y resaltados.
        
        Args:
            estado_tablero: Diccionario con toda la información del estado actual del juego
        """
        # Eliminar TODOS los elementos del lienzo excepto las etiquetas permanentes
        self.lienzo.delete("monton", "botones_juego", "revelado", "botones_menu")
        
        # Extraer información del estado del juego
        montones_visibles = estado_tablero['visible']           # Qué carta se ve en cada montón
        conteos_ocultos = estado_tablero['conteos_ocultos']     # Cuántas cartas ocultas hay en cada montón
        carta_actual = estado_tablero.get('carta_actual')       # La carta que se está jugando ahora
        revelacion_pendiente = estado_tablero.get('revelacion_pendiente')  # Si hay que revelar una carta

        # Crear botón para volver al menú principal durante el juego
        boton_menu = tk.Button(self, text="🏠 Menú Principal", 
                              command=self.controlador.terminar_juego_actual, 
                              bg="#4ECDC4", fg="black", font=("Arial", 9))
        self.lienzo.create_window(ANCHO_CANVAS - 80, 40, window=boton_menu, tags="botones_juego")

        # Dibujar cada uno de los 13 montones (1-12 en círculo, 13 en el centro)
        for i in range(1, 14):
            x, y = self.posiciones_montones[i]  # Obtener la posición de este montón
            
            # Resaltar el montón si hay que revelar una carta de él (borde verde lima)
            if revelacion_pendiente == i:
                self.lienzo.create_rectangle(x - 8, y - 8, x + ANCHO_CARTA + 8, y + ALTO_CARTA + 8, 
                                           fill="", outline="lime", width=5, tags="monton")
            # Resaltar el montón destino de la carta actual (borde naranja)
            elif carta_actual and self.obtener_destino_carta(carta_actual) == i:
                self.lienzo.create_rectangle(x - 6, y - 6, x + ANCHO_CARTA + 6, y + ALTO_CARTA + 6, 
                                           fill="", outline="orange", width=3, tags="monton")

            # Si hay cartas ocultas en este montón, dibujarlas como un mazo
            if conteos_ocultos.get(i, 0) > 0:
                # Dibujar hasta 5 cartas apiladas para mostrar el efecto de "montón"
                for j in range(min(conteos_ocultos[i], 5)):
                     self.lienzo.create_image(x - j * DESPLAZAMIENTO_MONTON_X, 
                                            y - j * DESPLAZAMIENTO_MONTON_Y, 
                                            image=self.recursos.obtener_imagen('back'), 
                                            anchor='nw', tags="monton")
                # Si hay más de una carta, mostrar el número total
                if conteos_ocultos[i] > 1:
                    self.lienzo.create_text(x + ANCHO_CARTA - 10, y + 10, 
                                          text=str(conteos_ocultos[i]), 
                                          fill="yellow", font=("Arial", 10, "bold"), tags="monton")

            # Dibujar la carta visible de este montón (si la hay)
            nombre_carta = montones_visibles.get(i, 'back')
            if nombre_carta != 'back':
                # Hay una carta visible, dibujarla
                imagen = self.recursos.obtener_imagen(nombre_carta)
                if imagen: 
                    self.lienzo.create_image(x, y, image=imagen, anchor='nw', tags="monton")
            elif conteos_ocultos.get(i, 0) == 0:
                # No hay cartas en este montón, dibujar un espacio vacío
                self.lienzo.create_rectangle(x, y, x + ANCHO_CARTA, y + ALTO_CARTA, 
                                           fill="darkgreen", outline="gray", dash=(5, 5), tags="monton")
            
            # Dibujar el número del montón encima de él
            self.lienzo.create_text(x + ANCHO_CARTA / 2, y - 15, text=str(i), 
                                  fill="white", font=("Arial", 12, "bold"), tags="monton")

        # Si hay una carta recién revelada, mostrarla con efectos especiales
        if self.carta_revelada and self.monton_revelado: 
            self.dibujar_carta_revelada()
            
        # Actualizar la información de la carta actual en la parte inferior
        self.actualizar_etiquetas_estado(carta_actual)

    def dibujar_carta_revelada(self):
        """
        Dibuja efectos especiales alrededor de una carta recién revelada.
        Esto ayuda al jugador a identificar cuál es la nueva carta en juego.
        """
        x_monton, y_monton = self.posiciones_montones[self.monton_revelado]
        desplazamiento_x, desplazamiento_y = -15, -15
        
        # Dibujar un borde amarillo alrededor del montón donde se reveló la carta
        self.lienzo.create_rectangle(x_monton - 5, y_monton - 5, 
                                   x_monton + ANCHO_CARTA + 5, y_monton + ALTO_CARTA + 5, 
                                   fill="", outline="yellow", width=4, tags="revelado")
        
        # Dibujar la carta revelada con un pequeño desplazamiento para que se vea claramente
        imagen = self.recursos.obtener_imagen(self.carta_revelada)
        if imagen: 
            self.lienzo.create_image(x_monton + desplazamiento_x, y_monton + desplazamiento_y, 
                                   image=imagen, anchor='nw', tags="revelado")
        
        # Mostrar hacia qué montón debe ir esta carta
        destino = self.obtener_destino_carta(self.carta_revelada)
        self.lienzo.create_text(x_monton + desplazamiento_x + ANCHO_CARTA/2, 
                              y_monton + desplazamiento_y + ALTO_CARTA + 15, 
                              text=f"→ Montón {destino}", fill="white", font=("Arial", 10, "bold"), tags="revelado")

    def mostrar_carta_revelada(self, carta, monton):
        """
        Establece qué carta se acaba de revelar para mostrarla con efectos especiales.
        
        Args:
            carta: El nombre de la carta revelada (ej: "A♠", "K♥")
            monton: El número del montón donde se reveló (1-13)
        """
        self.carta_revelada, self.monton_revelado = carta, monton
        self.dibujar_tablero(self.controlador.modelo.obtener_estado_tablero())

    def ocultar_carta_revelada(self):
        """
        Quita los efectos especiales de la carta revelada.
        """
        self.carta_revelada, self.monton_revelado = None, None

    def animar_movimiento_carta(self, carta, monton_origen, monton_destino, funcion_callback=None):
        """
        Anima el movimiento de una carta desde un montón hacia otro.
        Se usa en el modo automático para mostrar visualmente los movimientos.
        
        Args:
            carta: La carta que se está moviendo (ej: "A♠")
            monton_origen: Número del montón de donde sale la carta (1-13)
            monton_destino: Número del montón hacia donde va la carta (1-13)
            funcion_callback: Función a ejecutar cuando termine la animación
        """
        # Si ya hay una animación ejecutándose, ejecutar el callback y salir
        if self.animacion_ejecutandose:
            if funcion_callback: 
                funcion_callback()
            return
            
        self.animacion_ejecutandose = True
        
        # Obtener las coordenadas de los montones origen y destino
        x_origen, y_origen = self.posiciones_montones.get(monton_origen, (0,0))
        x_destino, y_destino = self.posiciones_montones.get(monton_destino, (0,0))
        
        # Obtener la imagen de la carta
        imagen = self.recursos.obtener_imagen(carta)
        if imagen:
            # Crear la carta que se va a animar
            carta_animada = self.lienzo.create_image(x_origen, y_origen, image=imagen, anchor='nw')
            
            # Configurar la animación (20 pasos para el movimiento)
            pasos = 20
            delta_x, delta_y = (x_destino - x_origen) / pasos, (y_destino - y_origen) / pasos
            
            def paso_movimiento(paso):
                """Función interna que ejecuta cada paso de la animación"""
                if paso < pasos:
                    # Mover la carta un paso más hacia el destino
                    self.lienzo.move(carta_animada, delta_x, delta_y)
                    # Programar el siguiente paso en 20 milisegundos
                    self.ventana_padre.after(20, lambda: paso_movimiento(paso + 1))
                else:
                    # La animación terminó
                    self.lienzo.delete(carta_animada)  # Eliminar la carta animada
                    self.animacion_ejecutandose = False
                    if funcion_callback: 
                        funcion_callback()  # Ejecutar lo que viene después
            
            paso_movimiento(0)  # Iniciar la animación
        else:
            # Si no se pudo cargar la imagen, terminar inmediatamente
            self.animacion_ejecutandose = False
            if funcion_callback: 
                funcion_callback()

    def animar_barajado(self, funcion_callback=None):
        """
        Crea una animación visual de cartas girando para simular el barajado.
        Es puramente decorativa pero hace que el juego se vea más profesional.
        
        Args:
            funcion_callback: Función a ejecutar cuando termine la animación (el barajado real)
        """
        # Si ya hay una animación ejecutándose, ejecutar el callback y salir
        if self.animacion_ejecutandose:
            if funcion_callback: 
                funcion_callback()
            return
            
        self.animacion_ejecutandose = True
        
        # Limpiar el lienzo pero mantener las etiquetas de texto
        self.lienzo.delete("all")
        self.lienzo.create_window(ANCHO_CANVAS / 2, 20, window=self.etiqueta_estado)
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.etiqueta_carta_actual)
        
        # Crear varias cartas que van a girar en círculo
        centro_x, centro_y = ANCHO_CANVAS / 2, ALTO_CANVAS / 2
        cartas = []
        
        # Crear 8 cartas en el centro, ligeramente desplazadas entre sí
        for i in range(8):
            imagen_carta = self.lienzo.create_image(
                centro_x + i * 2, centro_y + i * 2, 
                image=self.recursos.obtener_imagen('back'), 
                anchor='center', tags="animacion_barajado"
            )
            cartas.append(imagen_carta)
        
        paso = 0
        def paso_animacion():
            """Función interna que ejecuta cada paso de la animación de barajado"""
            nonlocal paso
            if paso > 40:  # La animación dura 40 pasos (aproximadamente 1.2 segundos)
                # Terminar la animación
                self.lienzo.delete("animacion_barajado")
                self.animacion_ejecutandose = False
                
                # Ejecutar el barajado real del juego
                if funcion_callback:
                    try:
                        funcion_callback()
                    except Exception as error:
                        print(f"Error en el callback del barajado: {error}")
                        # Si hay un error, al menos volver al menú principal
                        self.controlador.mostrar_menu_principal()
                return
            
            # Mover cada carta en un círculo
            for i, carta in enumerate(cartas):
                # Calcular la posición en el círculo para esta carta en este momento
                angulo = math.radians(paso * 9 + i * 45)  # Cada carta está separada 45 grados
                desplazamiento_x = 80 * math.cos(angulo)  # Radio de 80 píxeles
                desplazamiento_y = 80 * math.sin(angulo)
                # Mover la carta a su nueva posición
                self.lienzo.coords(carta, centro_x + desplazamiento_x, centro_y + desplazamiento_y)
            
            paso += 1
            # Programar el siguiente paso en 30 milisegundos (animación fluida)
            self.ventana_padre.after(30, paso_animacion)
        
        paso_animacion()  # Iniciar la animación

    def obtener_destino_carta(self, carta):
        """
        Calcula a qué montón debe ir una carta según las reglas del solitario reloj.
        
        Las reglas son:
        - As (A) va al montón 1
        - 2 va al montón 2
        - ... 
        - 10 va al montón 10
        - Jack (J) va al montón 11
        - Queen (Q) va al montón 12  
        - King (K) va al montón 13 (centro)
        
        Args:
            carta: El nombre de la carta (ej: "A♠", "K♥", "10♦")
            
        Returns:
            int: Número del montón donde debe ir la carta (1-13)
        """
        if not carta: 
            return None
            
        # Extraer el valor de la carta (todo excepto el último carácter que es el palo)
        valor = carta[:-1]
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        try: 
            # Buscar el valor en la lista y sumarle 1 (porque los montones van de 1 a 13)
            return valores.index(valor) + 1
        except ValueError: 
            # Si no se encuentra el valor, asumir que es un Rey y va al centro
            return 13

    def mostrar_mensaje_estado(self, mensaje):
        """
        Muestra un mensaje en la parte superior de la pantalla.
        
        Args:
            mensaje: El texto a mostrar (ej: "Modo Automático iniciado")
        """
        self.etiqueta_estado.config(text=mensaje)

    def actualizar_etiquetas_estado(self, carta_actual):
        """
        Actualiza la información de la carta actual en la parte inferior de la pantalla.
        
        Args:
            carta_actual: La carta que se está jugando ahora, o None si no hay ninguna
        """
        if carta_actual:
            destino = self.obtener_destino_carta(carta_actual)
            self.etiqueta_carta_actual.config(text=f"Carta Actual: {carta_actual} → Montón {destino}")
        else:
            self.etiqueta_carta_actual.config(text="No hay carta actual")

    def mostrar_mensaje_fin_juego(self, titulo, mensaje):
        """
        Muestra un cuadro de diálogo cuando el juego termina (victoria o derrota).
        
        Args:
            titulo: Título del cuadro de diálogo
            mensaje: Mensaje explicativo del resultado
        """
        messagebox.showinfo(titulo, mensaje)
        self.controlador.mostrar_menu_principal()

    def mostrar_menu(self):
        """
        Muestra el menú principal del juego con todos los botones de opciones.
        Este es el primer pantalla que ve el usuario y donde puede elegir qué hacer.
        """
        # Limpiar todo el lienzo
        self.lienzo.delete("all")
        
        # Configurar las etiquetas con el texto del menú
        self.etiqueta_estado.config(text="🎴 Solitario Reloj 🎴")
        self.etiqueta_carta_actual.config(text="Selecciona un modo de juego para comenzar")
        
        # Volver a crear las etiquetas en el lienzo (se borraron con delete("all"))
        self.lienzo.create_window(ANCHO_CANVAS / 2, 40, window=self.etiqueta_estado)
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.etiqueta_carta_actual)

        # Crear los botones del menú principal
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
        
        # Posicionar los botones en el centro de la pantalla con tags para poder eliminarlos después
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 - 100, window=boton_automatico, tags="botones_menu")
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 - 30, window=boton_manual, tags="botones_menu")
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 + 40, window=boton_barajar, tags="botones_menu")
        self.lienzo.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 + 110, window=boton_salir, tags="botones_menu")

    def _calcular_posiciones(self):
        """
        Calcula las posiciones de cada montón en la pantalla para formar un reloj.
        
        Los montones 1-12 se colocan en círculo como las horas de un reloj:
        - 12 arriba (como las 12 en punto)
        - 3 a la derecha (como las 3 en punto)
        - 6 abajo (como las 6 en punto)
        - 9 a la izquierda (como las 9 en punto)
        - etc.
        
        El montón 13 (Reyes) va en el centro.
        
        Returns:
            dict: Diccionario con las coordenadas de cada montón {1: (x, y), 2: (x, y), ...}
        """
        posiciones = {}
        centro_x, centro_y, radio = ANCHO_CANVAS / 2, ALTO_CANVAS / 2, 250
        
        # Calcular posiciones para montones 1-12 en forma de reloj
        for i in range(1, 13):
            # Calcular el ángulo para esta posición del reloj
            # -60 grados para que el 1 quede arriba a la derecha (como 1 en punto en un reloj)
            # i * 30 porque cada hora del reloj está separada 30 grados (360/12 = 30)
            angulo = math.radians(-60 + (i * 30))
            
            # Calcular coordenadas x, y usando trigonometría
            x = centro_x + radio * math.cos(angulo) - (ANCHO_CARTA / 2)
            y = centro_y + radio * math.sin(angulo) - (ALTO_CARTA / 2)
            posiciones[i] = (x, y)
        
        # Posición 13 (Reyes) en el centro exacto
        posiciones[13] = (centro_x - ANCHO_CARTA / 2, centro_y - ALTO_CARTA / 2)
        return posiciones

    def _identificar_monton(self, x, y):
        """
        Identifica en qué montón hizo clic el usuario basándose en las coordenadas del clic.
        
        Args:
            x: Coordenada horizontal del clic
            y: Coordenada vertical del clic
            
        Returns:
            int or None: Número del montón (1-13) o None si no hizo clic en ningún montón
        """
        # Revisar cada montón para ver si el clic fue dentro de sus límites
        for i, (pos_x, pos_y) in self.posiciones_montones.items():
            # Verificar si el clic está dentro del rectángulo de la carta
            if pos_x <= x <= pos_x + ANCHO_CARTA and pos_y <= y <= pos_y + ALTO_CARTA:
                return i
        return None  # No hizo clic en ningún montón