# gamemodel.py
import random

VALORES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
PALOS = ['♠', '♥', '♦', '♣']

class GameModel:
    def __init__(self):
        self.deck = []
        self.piles_hidden = {}
        self.piles_visible = {}
        self.is_game_over = True
        self.game_mode = None
        self.current_card = None  # La carta que se está jugando actualmente
        self.last_move_message = ""

    def shuffle_and_deal(self):
        """Crea una baraja, la baraja y la reparte en los montones."""
        self.deck = [f"{valor}{palo}" for valor in VALORES for palo in PALOS]
        random.shuffle(self.deck)
        
        self.piles_hidden = {i: [] for i in range(1, 14)}
        for i, card in enumerate(self.deck):
            pile_idx = (i % 13) + 1
            self.piles_hidden[pile_idx].append(card)
        
        # Todas las posiciones empiezan con cartas boca abajo
        self.piles_visible = {i: 'back' for i in range(1, 14)}
        
        # Revelar SOLO la primera carta del centro (posición 13) como carta actual
        if self.piles_hidden[13]:
            self.current_card = self.piles_hidden[13].pop(0)
            self.last_move_message = f"Inicio: Primera carta {self.current_card}. Debe ir al montón {self.get_card_destination(self.current_card)}."
        else:
            self.is_game_over = True
            self.last_move_message = "Error: No hay cartas en el centro."
            
        self.is_game_over = False


    def get_card_destination(self, card):
        """Obtiene el destino correcto para una carta según las reglas del reloj."""
        if not card or card == 'back':
            return None
        value = card[:-1]
        return VALORES.index(value) + 1

    def auto_play_step(self):
        """Ejecuta un paso del modo automático."""
        if not self.current_card or self.current_card == 'back':
            self.last_move_message = "No hay carta válida para mover."
            return False, self.last_move_message
            
        card_to_move = self.current_card
        destination = self.get_card_destination(card_to_move)
        
        # PASO 1: Colocar la carta actual en su destino correcto
        self.piles_visible[destination] = card_to_move
        
        # PASO 2: Revelar la siguiente carta del montón destino
        if self.piles_hidden[destination]:
            self.current_card = self.piles_hidden[destination].pop(0)
            self.last_move_message = f"Movió {card_to_move} al montón {destination}. Nueva carta: {self.current_card}"
            return True, self.last_move_message
        else:
            # Ya no hay cartas ocultas en el montón de destino
            self.current_card = None
            self.is_game_over = True
            self.last_move_message = f"Movió {card_to_move} al montón {destination}. No hay más cartas. Fin del juego."
            return False, self.last_move_message
            
    def manual_play_step(self, clicked_pile):
        """Ejecuta un paso del modo manual."""
        if not self.current_card:
            return False, "No hay carta para mover. El juego terminó."

        expected_destination = self.get_card_destination(self.current_card)
        
        if clicked_pile == expected_destination:
            # Ejecutar el mismo movimiento que en modo automático
            return self.auto_play_step()
        else:
            message = f"Movimiento incorrecto. La carta {self.current_card} debe ir al montón {expected_destination}."
            return False, message


    def check_game_status(self):
        """Verifica si se ha ganado o perdido. Retorna 'win', 'loss', 'ongoing'."""
        # Contar Reyes visibles
        kings_visible = sum(1 for card in self.piles_visible.values() 
                          if card != 'back' and card.startswith('K'))
        
        # Condición de derrota: 4 Reyes visibles
        if kings_visible >= 4:
            return 'loss'
            
        # Condición de victoria: todas las posiciones 1-13 tienen la carta correcta
        # Solo verificar si no hay carta actual (juego terminado)
        if not self.current_card:
            all_correct = True
            for i in range(1, 14):
                expected_value = VALORES[i-1]
                actual_card = self.piles_visible[i]
                if actual_card == 'back' or not actual_card.startswith(expected_value):
                    all_correct = False
                    break
            
            if all_correct:
                return 'win'
            else:
                return 'loss'  # Terminó sin completar correctamente
        
        # Si el juego se marcó como terminado por otra razón
        if self.is_game_over:
            return 'loss'
            
        return 'ongoing'

    def get_board_state(self):
        """Devuelve una representación del estado del tablero para la Vista."""
        return {
            'visible': self.piles_visible,
            'hidden_counts': {i: len(self.piles_hidden[i]) for i in range(1, 14)},
            'current_card': self.current_card,
            'message': self.last_move_message
        }