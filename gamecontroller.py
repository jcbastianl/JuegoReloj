# gamecontroller.py - Controlador del Juego Solitario Reloj
# Este archivo maneja la coordinación entre el modelo y la vista del juego

from gamemodel import ModeloJuego
from gameview import VistaJuego
from assets import GestorRecursos

class ControladorJuego:
    """
    Clase que actúa como intermediario entre el modelo (lógica del juego) 
    y la vista (interfaz gráfica). Se encarga de coordinar las acciones del usuario.
    """
    
    def __init__(self, ventana_padre):
        """
        Inicializa el controlador y todos los componentes del juego.
        
        Args:
            ventana_padre: La ventana principal de la aplicación
        """
        self.ventana_padre = ventana_padre
        self.modelo = ModeloJuego()                                  # La lógica del juego
        self.recursos = GestorRecursos()                             # Carga las imágenes de las cartas
        self.vista = VistaJuego(ventana_padre, self, self.recursos)  # La interfaz gráfica
        self.vista.pack(fill="both", expand=True)
        self.mostrar_menu_principal()

    def mostrar_menu_principal(self):
        """
        Muestra el menú principal y reinicia el estado del juego.
        """
        self.modelo.juego_terminado = True  # Marcar que no hay juego activo
        self.modelo.modo_juego = None       # Limpiar el modo de juego
        self.vista.mostrar_menu()           # Mostrar el menú en la vista

    def iniciar_juego_nuevo(self, modo):
        """
        Inicia un nuevo juego en el modo especificado (automático o manual).
        
        Args:
            modo: 'auto' para modo automático, 'manual' para modo manual
        """
        # 1. Configurar la lógica del juego en el modelo
        self.modelo.modo_juego = modo
        self.modelo.barajar_y_repartir()  # Barajar cartas y repartirlas en montones
        
        # 2. Actualizar la vista para mostrar el tablero
        self.actualizar_vista()

        # 3. Iniciar el modo de juego correspondiente
        if modo == 'auto':
            self.vista.mostrar_mensaje_estado("Modo Automático iniciado. Observa cómo se juega.")
            # Esperar 1 segundo antes de empezar para que el usuario vea el estado inicial
            self.ventana_padre.after(1000, self.ejecutar_turno_automatico)
        else:
            self.vista.mostrar_mensaje_estado("Modo Manual iniciado. Haz clic en el montón correcto.")

    def manejar_clic_monton(self, indice_monton):
        """
        Maneja cuando el usuario hace clic en un montón durante el modo manual.
        
        Args:
            indice_monton: Número del montón donde hizo clic (1-13)
        """
        # Si el juego terminó o no estamos en modo manual, ignorar el clic
        if self.modelo.juego_terminado or self.modelo.modo_juego != 'manual':
            return

        # Si hay una revelación pendiente, solo permitir clic en el montón correcto
        if self.modelo.revelacion_pendiente:
            if indice_monton == self.modelo.revelacion_pendiente:
                carta_revelada = self.modelo.intentar_revelar_de_monton(indice_monton)
                if carta_revelada:
                    self.vista.mostrar_carta_revelada(carta_revelada, indice_monton)
                    self.vista.mostrar_mensaje_estado(f"Nueva carta revelada: {carta_revelada}. ¡A jugar!")
                else:
                    self.modelo.juego_terminado = True
                    self.ventana_padre.after(500, self.verificar_fin_juego)
                self.actualizar_vista()
            else:
                self.vista.mostrar_mensaje_estado(f"Debes hacer clic en el montón {self.modelo.revelacion_pendiente} para revelar.")
            return

        # Lógica normal de movimiento
        exito, mensaje = self.modelo.ejecutar_paso_manual(indice_monton)
        self.vista.mostrar_mensaje_estado(mensaje)

        if exito:
            # Ocultar efectos de carta revelada anterior y actualizar
            self.vista.ocultar_carta_revelada()
            self.actualizar_vista()

        if self.modelo.juego_terminado:
            self.ventana_padre.after(1000, self.verificar_fin_juego)

    def ejecutar_turno_automatico(self):
        """
        Ejecuta un turno completo en modo automático.
        
        Proceso del turno automático:
        1. Verifica si hay una revelación pendiente y la maneja
        2. Toma una carta del mazo y la coloca en el montón correspondiente
        3. Maneja animaciones y mensajes de estado
        4. Programa el siguiente turno o termina el juego
        """
        # Verificar si el juego ya terminó
        if self.modelo.juego_terminado:
            self.verificar_fin_juego()
            return

        # Si no hay carta actual, el juego puede haber terminado
        if not self.modelo.carta_actual:
            self.verificar_fin_juego()
            return

        # Obtener información para la animación antes de mover
        carta_a_mover = self.modelo.carta_actual
        destino = self.modelo.obtener_destino_carta(carta_a_mover)
        origen = self.modelo.ultimo_movimiento_desde if self.modelo.ultimo_movimiento_desde is not None else 13
        
        # Ejecutar el paso automático en el modelo
        exito, mensaje = self.modelo.ejecutar_paso_automatico()

        def despues_animacion():
            """Función que se ejecuta después de completar la animación de movimiento"""
            self.vista.mostrar_mensaje_estado(mensaje)
            self.actualizar_vista()
            if not self.modelo.juego_terminado:
                # Continuar con el siguiente turno después de una pausa
                self.ventana_padre.after(800, self.ejecutar_turno_automatico)
            else:
                # Verificar el fin del juego después de una pausa
                self.ventana_padre.after(500, self.verificar_fin_juego)

        # Animar el movimiento de la carta
        self.vista.animar_movimiento_carta(carta_a_mover, origen, destino, despues_animacion)

    def actualizar_vista(self):
        """
        Actualiza la vista con el estado actual del modelo.
        
        Esta función:
        1. Obtiene el estado actual del tablero del modelo
        2. Actualiza el dibujo del tablero en la vista
        3. Actualiza las etiquetas de estado con la carta actual
        """
        estado_tablero = self.modelo.obtener_estado_tablero()
        self.vista.dibujar_tablero(estado_tablero)
        # Actualizar también la información de la carta actual
        carta_actual = estado_tablero.get('carta_actual')
        self.vista.actualizar_etiquetas_estado(carta_actual)

    def verificar_fin_juego(self):
        """
        Verifica si el juego ha terminado y muestra el resultado apropiado.
        
        Determina si el juego fue ganado o perdido y actualiza la interfaz
        con el mensaje correspondiente y opciones de menú.
        """
        if self.modelo.juego_terminado:
            estado = self.modelo.verificar_estado_juego()
            if estado == 'victoria':
                mensaje = "¡GANASTE! Todas las cartas están en su lugar correcto."
            else:
                mensaje = "¡Perdiste! Salieron los 4 Reyes antes de tiempo."
            
            self.vista.mostrar_mensaje_fin_juego("Juego Terminado", mensaje)
            return True
        return False
    
    def barajar_cartas(self):
        """
        Baraja las cartas con animación - solo permitido cuando no hay juego activo.
        
        Esta función:
        1. Verifica que no haya un juego en progreso
        2. Inicia la animación de barajado
        3. Baraja las cartas en el modelo después de la animación
        4. Muestra el nuevo orden en la consola
        5. Vuelve al menú principal
        """
        # Verificar si hay un juego en progreso
        if hasattr(self.modelo, 'modo_juego') and self.modelo.modo_juego and not self.modelo.juego_terminado:
            self.vista.mostrar_mensaje_estado("❌ No puedes barajar durante un juego activo. Termina el juego primero.")
            return
        
        # Mostrar mensaje de barajado
        self.vista.mostrar_mensaje_estado("🎲 Barajando cartas...")
        
        # Definir qué hacer después de la animación
        def despues_animacion_barajado():
            """Función que se ejecuta después de completar la animación de barajado"""
            try:
                # Baraja las cartas en el modelo
                self.modelo.barajar_y_repartir()
                
                # Imprimir orden de las cartas en consola para propósitos educativos
                print("\n" + "="*50)
                print("🎴 NUEVO ORDEN DE CARTAS DESPUÉS DEL BARAJADO:")
                print("="*50)
                
                for numero_monton in range(1, 14):
                    cartas_en_monton = self.modelo.montones_ocultos[numero_monton]
                    nombre_monton = self._obtener_nombre_monton(numero_monton)
                    print(f"Montón {numero_monton:2d} ({nombre_monton:>11}): {cartas_en_monton}")
                
                print("="*50)
                print(f"Total de cartas: {sum(len(monton) for monton in self.modelo.montones_ocultos.values())}")
                print("="*50 + "\n")
                
                # Volver al menú principal después de barajar
                self.mostrar_menu_principal()
                self.vista.mostrar_mensaje_estado("¡Cartas barajadas! Selecciona un modo de juego.")
                
            except Exception as e:
                print(f"Error en despues_animacion_barajado: {e}")
                # Si hay error, al menos volver al menú
                self.mostrar_menu_principal()
        
        # Iniciar la animación de barajado con callback
        self.vista.animar_barajado(funcion_callback=despues_animacion_barajado)

    def terminar_juego_actual(self):
        """
        Termina el juego actual y vuelve al menú principal.
        
        Esta función fuerza el fin del juego actual y regresa al usuario
        al menú principal para que pueda iniciar un nuevo juego.
        """
        self.modelo.juego_terminado = True
        self.modelo.modo_juego = None
        self.vista.mostrar_mensaje_estado("Juego terminado. ¡Vuelve a intentarlo!")
        self.ventana_padre.after(500, self.mostrar_menu_principal)

    def salir_juego(self):
        """
        Cierra la aplicación completamente.
        
        Termina la ejecución del programa y cierra la ventana principal.
        """
        self.ventana_padre.destroy()
    
    def mostrar_menu_principal(self):
        """
        Muestra el menú principal del juego.
        
        Resetea el estado del juego y muestra las opciones del menú principal
        para que el usuario pueda seleccionar un modo de juego.
        """
        # Resetear el estado del modelo
        self.modelo.reiniciar_juego()
        
        # Mostrar el menú en la vista
        self.vista.mostrar_menu()
    
    def _obtener_nombre_monton(self, numero_monton):
        """
        Convierte número de montón a nombre de posición en el reloj.
        
        Args:
            numero_monton: Número del montón (1-13)
            
        Returns:
            str: Nombre descriptivo de la posición en el reloj
        """
        nombres_reloj = {
            1: "1 (As)", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
            7: "7", 8: "8", 9: "9", 10: "10", 11: "J (Jack)",
            12: "Q (Queen)", 13: "K (Rey)"
        }
        return nombres_reloj.get(numero_monton, str(numero_monton))