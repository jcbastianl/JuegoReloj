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
        self.pending_reveal = None  # Para el modo manual: montón del cual se debe revelar
        self.last_move_from = None  # Desde qué montón se movió la última carta

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
        if not self.current_card:
            self.last_move_message = "No hay carta válida para mover."
            return False, self.last_move_message
            
        card_to_move = self.current_card
        destination = self.get_card_destination(card_to_move)
        self.last_move_from = destination
        
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
            
    def reveal_next_card(self, pile_index):
        """Revela la siguiente carta de un montón específico"""
        if self.piles_hidden[pile_index]:
            card = self.piles_hidden[pile_index].pop(0)
            self.current_card = card
            self.pending_reveal = None
            self.last_move_message = f"Nueva carta revelada: {card}"
            return card
        else:
            self.current_card = None
            self.is_game_over = True
            self.last_move_message = f"No hay más cartas en el montón {pile_index}. Fin del juego."
            return None

    def manual_play_step(self, clicked_pile):
        """Ejecuta un paso del modo manual."""
        if not self.current_card:
            return False, "No hay carta para mover. El juego terminó."

        expected_destination = self.get_card_destination(self.current_card)
        
        if clicked_pile == expected_destination:
            # Mover la carta a su destino
            card_to_move = self.current_card
            self.piles_visible[expected_destination] = card_to_move
            self.last_move_from = expected_destination
            
            # Preparar para revelar la siguiente carta
            self.pending_reveal = expected_destination
            self.current_card = None  # Temporalmente sin carta actual
            
            message = f"Carta {card_to_move} colocada en montón {expected_destination}. Haz clic para revelar la siguiente."
            return True, message
        else:
            message = f"Movimiento incorrecto. La carta {self.current_card} debe ir al montón {expected_destination}."
            return False, message

    def complete_manual_move(self):
        """Completa el movimiento manual revelando la siguiente carta"""
        if self.pending_reveal:
            return self.reveal_next_card(self.pending_reveal)
        return None


    def check_game_status(self):
        """Verifica si se ha ganado o perdido. Retorna 'win', 'loss', 'ongoing'."""
        # Contar Reyes visibles
        kings_visible = sum(1 for card in self.piles_visible.values() 
                          if card != 'back' and card.startswith('K'))
        
        # Condición de derrota: 4 Reyes visibles
        if kings_visible >= 4:
            return 'loss'
            
        # Solo verificar victoria si el juego terminó (no hay carta actual)
        if not self.current_card and self.is_game_over:
            # Verificar que todas las posiciones tengan la carta correcta
            all_correct = True
            total_cards_placed = 0
            
            for i in range(1, 14):
                expected_value = VALORES[i-1]
                actual_card = self.piles_visible[i]
                
                if actual_card != 'back':
                    total_cards_placed += 1
                    if not actual_card.startswith(expected_value):
                        all_correct = False
                        break
                else:
                    all_correct = False
                    break
            
            # Solo es victoria si todas las 52 cartas están colocadas correctamente
            total_hidden = sum(len(pile) for pile in self.piles_hidden.values())
            
            if all_correct and total_cards_placed == 13 and total_hidden == 0:
                return 'win'
            else:
                return 'loss'
        
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
            'message': self.last_move_message,
            'pending_reveal': self.pending_reveal,
            'last_move_from': self.last_move_from
        }