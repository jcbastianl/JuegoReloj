# gamemodel.py - Modelo del Juego Solitario Reloj
# Este archivo contiene toda la lógica del juego, las reglas y el estado del juego

import random

# Definición de constantes del juego
VALORES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
PALOS = ['♠', '♥', '♦', '♣']

class ModeloJuego:
    """
    Clase que representa el modelo del juego Solitario Reloj.
    
    Maneja toda la lógica del juego incluyendo:
    - Estado del tablero (montones de cartas)
    - Reglas del juego (dónde colocar cada carta)
    - Movimientos automáticos y manuales
    - Condiciones de victoria y derrota
    """
    
    def __init__(self):
        """
        Inicializa el modelo del juego con su estado inicial.
        
        El juego comienza sin cartas repartidas, esperando que el usuario
        inicie un nuevo juego.
        """
        self.mazo = []  # Lista de todas las cartas de la baraja
        self.montones_ocultos = {}  # Cartas boca abajo en cada montón (1-13)
        self.montones_visibles = {}  # Carta visible en cada montón (o 'back' si no hay)
        self.juego_terminado = True  # El juego inicia terminado hasta que se empiece uno nuevo
        self.modo_juego = None  # 'auto' para automático, 'manual' para manual
        self.carta_actual = None  # La carta que se está jugando actualmente
        self.mensaje_ultimo_movimiento = ""  # Mensaje del último movimiento realizado
        self.revelacion_pendiente = None  # Para modo manual: montón del cual se debe revelar
        self.ultimo_movimiento_desde = None  # Desde qué montón se movió la última carta

    def barajar_y_repartir(self):
        """
        Crea una baraja completa, la baraja aleatoriamente y la reparte en 13 montones.
        
        Proceso de repartición:
        1. Crea una baraja de 52 cartas (13 valores × 4 palos)
        2. Baraja las cartas aleatoriamente
        3. Reparte las cartas en 13 montones de forma circular
        4. Todas las cartas empiezan boca abajo
        5. Revela la primera carta del centro (montón 13) como carta inicial
        """
        # Crear baraja completa
        self.mazo = [f"{valor}{palo}" for valor in VALORES for palo in PALOS]
        random.shuffle(self.mazo)
        
        # Inicializar los 13 montones vacíos
        self.montones_ocultos = {i: [] for i in range(1, 14)}
        
        # Repartir las cartas de forma circular en los 13 montones
        for i, carta in enumerate(self.mazo):
            indice_monton = (i % 13) + 1
            self.montones_ocultos[indice_monton].append(carta)
        
        # Todas las posiciones empiezan con cartas boca abajo
        self.montones_visibles = {i: 'back' for i in range(1, 14)}
        
        # Revelar SOLO la primera carta del centro (posición 13) como carta actual
        if self.montones_ocultos[13]:
            self.carta_actual = self.montones_ocultos[13].pop(0)
            self.mensaje_ultimo_movimiento = f"Inicio: Primera carta {self.carta_actual}. Debe ir al montón {self.obtener_destino_carta(self.carta_actual)}."
        else:
            self.juego_terminado = True
            self.mensaje_ultimo_movimiento = "Error: No hay cartas en el centro."
            
        self.juego_terminado = False

    def obtener_destino_carta(self, carta):
        """
        Obtiene el destino correcto para una carta según las reglas del Solitario Reloj.
        
        Reglas:
        - As (A) va al montón 1
        - Números 2-10 van a sus montones correspondientes
        - Jack (J) va al montón 11
        - Queen (Q) va al montón 12  
        - King (K) va al montón 13 (centro)
        
        Args:
            carta: String representando la carta (ej: "A♠", "K♥", "10♦")
            
        Returns:
            int: Número del montón destino (1-13), o None si la carta no es válida
        """
        if not carta or carta == 'back':
            return None
        valor = carta[:-1]  # Extraer el valor sin el palo
        return VALORES.index(valor) + 1

    def ejecutar_paso_automatico(self):
        """
        Ejecuta un paso completo del modo automático.
        
        Proceso automático:
        1. Toma la carta actual y la coloca en su montón destino correcto
        2. Revela la siguiente carta del montón destino
        3. Actualiza el estado del juego
        
        Returns:
            tuple: (exito, mensaje) donde:
                - exito: True si el movimiento fue exitoso, False si el juego terminó
                - mensaje: Descripción del movimiento realizado
        """
        if not self.carta_actual:
            self.mensaje_ultimo_movimiento = "No hay carta válida para mover."
            return False, self.mensaje_ultimo_movimiento
            
        carta_a_mover = self.carta_actual
        destino = self.obtener_destino_carta(carta_a_mover)
        self.ultimo_movimiento_desde = destino
        
        # PASO 1: Colocar la carta actual en su destino correcto
        self.montones_visibles[destino] = carta_a_mover
        
        # PASO 2: Revelar la siguiente carta del montón destino
        if self.montones_ocultos[destino]:
            self.carta_actual = self.montones_ocultos[destino].pop(0)
            self.mensaje_ultimo_movimiento = f"Movió {carta_a_mover} al montón {destino}. Nueva carta: {self.carta_actual}"
            return True, self.mensaje_ultimo_movimiento
        else:
            # Ya no hay cartas ocultas en el montón de destino
            self.carta_actual = None
            self.juego_terminado = True
            self.mensaje_ultimo_movimiento = f"Movió {carta_a_mover} al montón {destino}. No hay más cartas. Fin del juego."
            return False, self.mensaje_ultimo_movimiento
            
    def revelar_siguiente_carta(self, indice_monton):
        """
        Revela la siguiente carta de un montón específico.
        
        Args:
            indice_monton: Número del montón del cual revelar la carta (1-13)
            
        Returns:
            str: La carta revelada, o None si no hay más cartas
        """
        if self.montones_ocultos[indice_monton]:
            carta = self.montones_ocultos[indice_monton].pop(0)
            self.carta_actual = carta
            self.revelacion_pendiente = None
            self.mensaje_ultimo_movimiento = f"Nueva carta revelada: {carta}"
            return carta
        else:
            self.carta_actual = None
            self.juego_terminado = True
            self.mensaje_ultimo_movimiento = f"No hay más cartas en el montón {indice_monton}. Fin del juego."
            return None

    def ejecutar_paso_manual(self, monton_clickeado):
        """
        Ejecuta un paso del modo manual basado en el clic del usuario.
        
        En modo manual, el usuario debe hacer clic en el montón correcto
        donde debe ir la carta actual.
        
        Args:
            monton_clickeado: Número del montón donde hizo clic el usuario
            
        Returns:
            tuple: (exito, mensaje) describiendo el resultado del movimiento
        """
        if not self.carta_actual:
            return False, "No hay carta para mover. El juego terminó."

        destino_esperado = self.obtener_destino_carta(self.carta_actual)
        
        if monton_clickeado == destino_esperado:
            # Mover la carta a su destino correcto
            carta_a_mover = self.carta_actual
            self.montones_visibles[destino_esperado] = carta_a_mover
            self.ultimo_movimiento_desde = destino_esperado
            
            # Preparar para revelar la siguiente carta DESDE EL MISMO MONTÓN
            self.revelacion_pendiente = destino_esperado
            self.carta_actual = None  # Temporalmente sin carta actual
            
            mensaje = f"Carta {carta_a_mover} colocada en montón {destino_esperado}. Haz clic en el montón {destino_esperado} para revelar la siguiente."
            return True, mensaje
        else:
            mensaje = f"Movimiento incorrecto. La carta {self.carta_actual} debe ir al montón {destino_esperado}."
            return False, mensaje

    def intentar_revelar_de_monton(self, monton_clickeado):
        """
        Intenta revelar una carta del montón especificado (solo si es el correcto).
        
        Args:
            monton_clickeado: Número del montón donde se hizo clic
            
        Returns:
            str: La carta revelada si el clic fue correcto, None en caso contrario
        """
        if self.revelacion_pendiente and monton_clickeado == self.revelacion_pendiente:
            return self.revelar_siguiente_carta(self.revelacion_pendiente)
        return None

    def verificar_estado_juego(self):
        """
        Verifica el estado actual del juego para determinar victoria, derrota o continuación.
        
        Condiciones:
        - Victoria: Todas las cartas están en sus posiciones correctas
        - Derrota: Los 4 Reyes están visibles antes de completar el juego
        - En progreso: El juego puede continuar
        
        Returns:
            str: 'victoria', 'derrota', o 'en_progreso'
        """
        # Contar Reyes visibles
        reyes_visibles = sum(1 for carta in self.montones_visibles.values() 
                          if carta != 'back' and carta.startswith('K'))
        
        # Condición de derrota: 4 Reyes visibles
        if reyes_visibles >= 4:
            return 'derrota'
            
        # Solo verificar victoria si el juego terminó (no hay carta actual)
        if not self.carta_actual and self.juego_terminado:
            # Verificar que todas las posiciones tengan la carta correcta
            todas_correctas = True
            total_cartas_colocadas = 0
            
            for i in range(1, 14):
                valor_esperado = VALORES[i-1]
                carta_actual = self.montones_visibles[i]
                
                if carta_actual != 'back':
                    total_cartas_colocadas += 1
                    if not carta_actual.startswith(valor_esperado):
                        todas_correctas = False
                        break
                else:
                    todas_correctas = False
                    break
            
            # Solo es victoria si todas las 52 cartas están colocadas correctamente
            total_ocultas = sum(len(monton) for monton in self.montones_ocultos.values())
            
            if todas_correctas and total_cartas_colocadas == 13 and total_ocultas == 0:
                return 'victoria'
            else:
                return 'derrota'
        
        # Si el juego se marcó como terminado por otra razón
        if self.juego_terminado:
            return 'derrota'
            
        return 'en_progreso'

    def verificar_victoria(self):
        """
        Método específico para verificar si el juego fue ganado.
        
        Returns:
            bool: True si el juego fue ganado, False en caso contrario
        """
        return self.verificar_estado_juego() == 'victoria'

    def obtener_estado_tablero(self):
      
        return {
            'visible': self.montones_visibles,
            'conteos_ocultos': {i: len(self.montones_ocultos[i]) for i in range(1, 14)},
            'carta_actual': self.carta_actual,
            'mensaje': self.mensaje_ultimo_movimiento,
            'revelacion_pendiente': self.revelacion_pendiente,
            'ultimo_movimiento_desde': self.ultimo_movimiento_desde
        }

    def reiniciar_juego(self):
      
        self.mazo = []
        self.montones_ocultos = {}
        self.montones_visibles = {}
        self.juego_terminado = True
        self.modo_juego = None
        self.carta_actual = None
        self.mensaje_ultimo_movimiento = ""
        self.revelacion_pendiente = None
        self.ultimo_movimiento_desde = None