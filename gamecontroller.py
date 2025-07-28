# gamecontroller.py - Controlador del Juego Solitario Reloj

from gamemodel import ModeloJuego
from gameview import VistaJuego
from assets import GestorRecursos

class ControladorJuego:
    # Intermediario entre el modelo y la vista
    
    def __init__(self, ventana_padre):
        # Inicializar componentes del juego
        self.ventana_padre = ventana_padre
        self.modelo = ModeloJuego()
        self.recursos = GestorRecursos()
        self.vista = VistaJuego(ventana_padre, self, self.recursos)
        self.vista.pack(fill="both", expand=True)
        self.mostrar_menu_principal()

    def mostrar_menu_principal(self):
        # Mostrar menú principal
        self.modelo.juego_terminado = True
        self.modelo.modo_juego = None
        self.vista.mostrar_menu()

    def iniciar_juego_nuevo(self, modo):
        # Iniciar nuevo juego en el modo especificado
        self.modelo.modo_juego = modo
        self.modelo.barajar_y_repartir()
        self.actualizar_vista()

        if modo == 'auto':
            self.vista.mostrar_mensaje_estado("Modo Automático iniciado. Observa cómo se juega.")
            self.ventana_padre.after(1000, self.ejecutar_turno_automatico)
        else:
            self.vista.mostrar_mensaje_estado("Modo Manual iniciado. Haz clic en el montón correcto.")

    def manejar_clic_monton(self, indice_monton):
        # Manejar clics en montones durante modo manual
        if self.modelo.juego_terminado or self.modelo.modo_juego != 'manual':
            return

        # Si hay revelación pendiente
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
            self.vista.ocultar_carta_revelada()
            self.actualizar_vista()

        if self.modelo.juego_terminado:
            self.ventana_padre.after(1000, self.verificar_fin_juego)

    def ejecutar_turno_automatico(self):
        # Ejecutar turno en modo automático
        if self.modelo.juego_terminado:
            self.verificar_fin_juego()
            return

        if not self.modelo.carta_actual:
            self.verificar_fin_juego()
            return

        # Obtener info para animación
        carta_a_mover = self.modelo.carta_actual
        destino = self.modelo.obtener_destino_carta(carta_a_mover)
        origen = self.modelo.ultimo_movimiento_desde if self.modelo.ultimo_movimiento_desde is not None else 13
        
        exito, mensaje = self.modelo.ejecutar_paso_automatico()

        def despues_animacion():
            self.vista.mostrar_mensaje_estado(mensaje)
            self.actualizar_vista()
            if not self.modelo.juego_terminado:
                self.ventana_padre.after(800, self.ejecutar_turno_automatico)
            else:
                self.ventana_padre.after(500, self.verificar_fin_juego)

        self.vista.animar_movimiento_carta(carta_a_mover, origen, destino, despues_animacion)

    def actualizar_vista(self):
        # Actualizar vista con estado actual
        estado_tablero = self.modelo.obtener_estado_tablero()
        self.vista.dibujar_tablero(estado_tablero)
        carta_actual = estado_tablero.get('carta_actual')
        self.vista.actualizar_etiquetas_estado(carta_actual)

    def verificar_fin_juego(self):
        # Verificar si terminó el juego
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
        # Barajar cartas con animación
        if hasattr(self.modelo, 'modo_juego') and self.modelo.modo_juego and not self.modelo.juego_terminado:
            self.vista.mostrar_mensaje_estado("❌ No puedes barajar durante un juego activo. Termina el juego primero.")
            return
        
        self.vista.mostrar_mensaje_estado("🎲 Barajando cartas...")
        
        def despues_animacion_barajado():
            try:
                self.modelo.barajar_y_repartir()
                
                # Imprimir orden en consola
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
                
                self.mostrar_menu_principal()
                self.vista.mostrar_mensaje_estado("¡Cartas barajadas! Selecciona un modo de juego.")
                
            except Exception as e:
                print(f"Error en despues_animacion_barajado: {e}")
                self.mostrar_menu_principal()
        
        self.vista.animar_barajado(funcion_callback=despues_animacion_barajado)

    def terminar_juego_actual(self):
        # Terminar juego actual y volver al menú
        self.modelo.juego_terminado = True
        self.modelo.modo_juego = None
        self.vista.mostrar_mensaje_estado("Juego terminado. ¡Vuelve a intentarlo!")
        self.ventana_padre.after(500, self.mostrar_menu_principal)

    def salir_juego(self):
        # Cerrar la aplicación
        self.ventana_padre.destroy()
    
    def mostrar_menu_principal(self):
        # Mostrar menú principal
        self.modelo.reiniciar_juego()
        self.vista.mostrar_menu()
    
    def _obtener_nombre_monton(self, numero_monton):
        # Convertir número de montón a nombre
        nombres_reloj = {
            1: "1 (As)", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
            7: "7", 8: "8", 9: "9", 10: "10", 11: "J (Jack)",
            12: "Q (Queen)", 13: "K (Rey)"
        }
        return nombres_reloj.get(numero_monton, str(numero_monton))