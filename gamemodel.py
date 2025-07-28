# gamemodel.py - Modelo del Juego Solitario Reloj

import random


VALORES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
PALOS = ['♠', '♥', '♦', '♣']

class ModeloJuego:
  
    
    def __init__(self):
        # Inicializar variables del juego
        self.mazo = []
        self.montones_ocultos = {}
        self.montones_visibles = {}
        self.juego_terminado = True
        self.modo_juego = None
        self.carta_actual = None
        self.mensaje_ultimo_movimiento = ""
        self.revelacion_pendiente = None
        self.ultimo_movimiento_desde = None

    def barajar_y_repartir(self):
        #Crea baraja 
        self.mazo = [f"{valor}{palo}" for valor in VALORES for palo in PALOS]
        
        # self._ordenar_para_ganar()
        # return
        
        self._barajado_riffle()
        
        # Iniac montones va
        self.montones_ocultos = {i: [] for i in range(1, 14)}
        
        # Repartizao
        for i, carta in enumerate(self.mazo):
            indice_monton = (i % 13) + 1
            self.montones_ocultos[indice_monton].append(carta)
        
        # reverso
        self.montones_visibles = {i: 'back' for i in range(1, 14)}
        
        # Revelar primera carta del centro como carta actual
        if self.montones_ocultos[13]:
            self.carta_actual = self.montones_ocultos[13].pop(0)
            # self.mensaje_ultimo_movimiento = f"Inicio: Primera carta {self.carta_actual}. Debe ir al montón {self.obtener_destino_carta(self.carta_actual)}."
            self.mensaje_ultimo_movimiento = "¿Voy a pasar Análisis Numérico?"
        else:
            self.juego_terminado = True
            # self.mensaje_ultimo_movimiento = "Error: No hay cartas en el centro."
            self.mensaje_ultimo_movimiento = "¿Voy a pasar Análisis Numérico?"
            
        self.juego_terminado = False

    def _barajado_riffle(self):
       
        total_cartas = len(self.mazo)
       
        mitad = total_cartas // 2
        variacion = random.randint(-5, 5)
        punto_corte = mitad + variacion
        
      
        mitad1 = self.mazo[:punto_corte]
        mitad2 = self.mazo[punto_corte:]
        
        # Paso 2: Combinar de forma irregular
        mazo_barajado = []
        i, j = 0, 0  # Índices para cada mitad
        
        while i < len(mitad1) and j < len(mitad2):
            # Decidir cuántas cartas tomar de cada mitad (1-3 cartas)
            cartas_mitad1 = random.randint(1, 3)
            cartas_mitad2 = random.randint(1, 3)
            
            # Tomar cartas de la mitad 1
            for _ in range(cartas_mitad1):
                if i < len(mitad1):
                    mazo_barajado.append(mitad1[i])
                    i += 1
            
            # Tomar cartas de la mitad 2
            for _ in range(cartas_mitad2):
                if j < len(mitad2):
                    mazo_barajado.append(mitad2[j])
                    j += 1
        
        #agrega las que queden
        while i < len(mitad1):
            mazo_barajado.append(mitad1[i])
            i += 1
        while j < len(mitad2):
            mazo_barajado.append(mitad2[j])
            j += 1
        
        self.mazo = mazo_barajado

    def obtener_destino_carta(self, carta):
        if not carta or carta == 'back':
            return None
        valor = carta[:-1]
        return VALORES.index(valor) + 1

    def ejecutar_paso_automatico(self):
        
        if not self.carta_actual:
            self.mensaje_ultimo_movimiento = "No hay carta válida para mover."
            return False, self.mensaje_ultimo_movimiento
            
        carta_a_mover = self.carta_actual
        destino = self.obtener_destino_carta(carta_a_mover)
        self.ultimo_movimiento_desde = destino
        
        # Colocar carta en su destino
        self.montones_visibles[destino] = carta_a_mover
        
        # Revelar siguiente carta del montón destino
        if self.montones_ocultos[destino]:
            self.carta_actual = self.montones_ocultos[destino].pop(0)
            # self.mensaje_ultimo_movimiento = f"Movió {carta_a_mover} al montón {destino}. Nueva carta: {self.carta_actual}"
            self.mensaje_ultimo_movimiento = "¿Voy a pasar Análisis Numérico?"
            return True, self.mensaje_ultimo_movimiento
        else:
            self.carta_actual = None
            self.juego_terminado = True
            # self.mensaje_ultimo_movimiento = f"Movió {carta_a_mover} al montón {destino}. No hay más cartas. Fin del juego."
            self.mensaje_ultimo_movimiento = "¿Voy a pasar Análisis Numérico?"
            return False, self.mensaje_ultimo_movimiento
            
    def revelar_siguiente_carta(self, indice_monton):
        # Revelar siguiente carta de un montón
        if self.montones_ocultos[indice_monton]:
            carta = self.montones_ocultos[indice_monton].pop(0)
            self.carta_actual = carta
            self.revelacion_pendiente = None
            # self.mensaje_ultimo_movimiento = f"Nueva carta revelada: {carta}"
            self.mensaje_ultimo_movimiento = "¿Voy a pasar Análisis Numérico?"
            return carta
        else:
            self.carta_actual = None
            self.juego_terminado = True
            # self.mensaje_ultimo_movimiento = f"No hay más cartas en el montón {indice_monton}. Fin del juego."
            self.mensaje_ultimo_movimiento = "¿Voy a pasar Análisis Numérico?"
            return None

    def ejecutar_paso_manual(self, monton_clickeado):
        # Ejecutar paso manual según clic del usuario
        if not self.carta_actual:
            return False, "No hay carta para mover. El juego terminó."

        destino_esperado = self.obtener_destino_carta(self.carta_actual)
        
        if monton_clickeado == destino_esperado:
            # Mover carta a su destino
            carta_a_mover = self.carta_actual
            self.montones_visibles[destino_esperado] = carta_a_mover
            self.ultimo_movimiento_desde = destino_esperado
            
            # Preparar revelación desde el mismo montón
            self.revelacion_pendiente = destino_esperado
            self.carta_actual = None
            
            mensaje = f"Carta {carta_a_mover} colocada en montón {destino_esperado}. Haz clic en el montón {destino_esperado} para revelar la siguiente."
            return True, mensaje
        else:
            mensaje = f"Movimiento incorrecto. La carta {self.carta_actual} debe ir al montón {destino_esperado}."
            return False, mensaje

    def intentar_revelar_de_monton(self, monton_clickeado):
        # Intentar revelar carta del montón correcto
        if self.revelacion_pendiente and monton_clickeado == self.revelacion_pendiente:
            return self.revelar_siguiente_carta(self.revelacion_pendiente)
        return None

    def verificar_estado_juego(self):
      
        if not self.montones_visibles:
            return 'en_progreso'
            
        # Contar Reyes visibles
        reyes_visibles = sum(1 for carta in self.montones_visibles.values() 
                          if carta != 'back' and carta.startswith('K'))
        
        # Derrota: 4 Reyes visibles
        if reyes_visibles >= 4:
            return 'derrota'
            
        # Veifica victoria en base a carta activa
        if not self.carta_actual and self.juego_terminado:
            todas_correctas = True
            total_cartas_colocadas = 0
            
            for i in range(1, 14):
                valor_esperado = VALORES[i-1]
                carta_actual = self.montones_visibles.get(i, 'back')
                
                if carta_actual != 'back':
                    total_cartas_colocadas += 1
                    if not carta_actual.startswith(valor_esperado):
                        todas_correctas = False
                        break
                else:
                    todas_correctas = False
                    break
            
            total_ocultas = sum(len(monton) for monton in self.montones_ocultos.values())
            
            if todas_correctas and total_cartas_colocadas == 13 and total_ocultas == 0:
                return 'victoria'
            else:
                return 'derrota'
        
        if self.juego_terminado:
            return 'derrota'
            
        return 'en_progreso'

    def verificar_victoria(self):
        # Verificar si el juego fue ganado
        return self.verificar_estado_juego() == 'victoria'

    def obtener_estado_tablero(self):
        # Obtener estado actual del tablero
        return {
            'visible': self.montones_visibles,
            'conteos_ocultos': {i: len(self.montones_ocultos[i]) for i in range(1, 14)},
            'carta_actual': self.carta_actual,
            'mensaje': self.mensaje_ultimo_movimiento,
            'revelacion_pendiente': self.revelacion_pendiente,
            'ultimo_movimiento_desde': self.ultimo_movimiento_desde
        }

    def reiniciar_juego(self):
        # Reiniciar todas las variables del juego
        self.mazo = []
        self.montones_ocultos = {}
        self.montones_visibles = {}
        self.juego_terminado = True
        self.modo_juego = None
        self.carta_actual = None
        self.mensaje_ultimo_movimiento = ""
        self.revelacion_pendiente = None
        self.ultimo_movimiento_desde = None
    
    def _ordenar_para_ganar(self):
        
        # Inicializar montones vacíos
        self.montones_ocultos = {i: [] for i in range(1, 14)}
        self.montones_visibles = {i: 'back' for i in range(1, 14)}
        
        # Crear una baraja simple que garantice victoria
        # Solo usar cartas A, 2, 3 para que sea fácil de ganar
        cartas_faciles = [
            "A♠", "2♠", "3♠",  # Montón 1, 2, 3
            "A♥", "2♥", "3♥",  # Repetir para más cartas
            "A♦", "2♦", "3♦",
            "A♣", "2♣", "3♣",
            "A♠"  # Carta inicial en el centro
        ]
        
        # Repartir las cartas fáciles
        self.mazo = cartas_faciles
        for i, carta in enumerate(self.mazo):
            indice_monton = (i % 13) + 1
            self.montones_ocultos[indice_monton].append(carta)
        
        # Revelar primera carta del centro
        if self.montones_ocultos[13]:
            self.carta_actual = self.montones_ocultos[13].pop(0)
            self.mensaje_ultimo_movimiento = "¿Voy a pasar Análisis Numérico?"
        
        self.juego_terminado = False