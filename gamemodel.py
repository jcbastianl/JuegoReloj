# model.py
import random

VALORES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
PALOS = ['♠', '♥', '♦', '♣']

class GameModel:
    def __init__(self):
        self.deck = []
        self.piles_hidden = {}
        self.piles_visible = {}
        self.selected_card_info = None # p. ej., (origen_idx, carta)
        self.is_game_over = True
        self.game_mode = None
        self.current_card = None  # La carta que se está jugando actualmente

    def shuffle_and_deal(self):
        """Crea una baraja, la baraja y la reparte en los montones."""
        self.deck = [f"{valor}{palo}" for valor in VALORES for palo in PALOS]
        # Usar un barajado realista o simple
        random.shuffle(self.deck)
        
        self.piles_hidden = {i: [] for i in range(1, 14)}
        for i, card in enumerate(self.deck):
            pile_idx = (i % 13) + 1
            self.piles_hidden[pile_idx].append(card)
        
        # Todas las posiciones empiezan con cartas boca abajo excepto el centro
        self.piles_visible = {i: 'back' for i in range(1, 14)}
        
        # Revelar la primera carta del centro (posición 13)
        if self.piles_hidden[13]:
            self.piles_visible[13] = self.piles_hidden[13].pop(0)
        
        self.is_game_over = False
        self.selected_card_info = None
        self.current_card = self.piles_visible[13]  # La carta actual en juego

    def reveal_card(self, pile_index):
        """Revela una carta de un montón si hay cartas ocultas."""
        if self.piles_hidden[pile_index]:
            card = self.piles_hidden[pile_index].pop(0)
            self.piles_visible[pile_index] = card
            return card
        return None

    def get_card_destination(self, card):
        """Obtiene el destino correcto para una carta según las reglas del reloj"""
        if not card or card == 'back':
            return None
        
        value = card[:-1]  # Remover el palo
        
        # Mapeo de valores a posiciones
        value_to_position = {
            'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
        }
        
        return value_to_position.get(value, 13)

    def make_move(self, card):
        """Realiza un movimiento según las reglas del solitario reloj"""
        if not card or card == 'back':
            return False, "No hay carta válida para mover"
        
        destination = self.get_card_destination(card)
        
        # Verificar si el montón destino tiene cartas ocultas
        if not self.piles_hidden[destination]:
            # Si no hay cartas ocultas en el destino, el juego puede terminar
            if destination == 13:  # Rey va al centro
                return False, f"No hay más cartas en el centro. Rey {card} termina el juego."
            else:
                return False, f"No hay más cartas en el montón {destination}. Juego terminado."
        
        # Mover la carta al montón destino
        next_card = self.piles_hidden[destination].pop(0)
        self.piles_visible[destination] = card
        
        # La siguiente carta a jugar es la que se reveló
        self.current_card = next_card
        
        return True, f"Carta {card} movida a posición {destination}. Nueva carta: {next_card}"

    def auto_play_step(self):
        """Ejecuta un paso del modo automático"""
        if not self.current_card or self.current_card == 'back':
            return False, "No hay carta actual para jugar"
        
        return self.make_move(self.current_card)

    def check_win_loss_condition(self):
        """
        Verifica si se ha ganado o perdido el juego.
        Retorna un estado: 'win', 'loss', 'ongoing'.
        """
        # Condición de derrota: 4 Reyes visibles
        visible_kings = sum(1 for card in self.piles_visible.values() 
                          if card and card.startswith('K'))
        
        if visible_kings >= 4:
            return 'loss'

        # Condición de victoria: todas las cartas están reveladas en sus posiciones correctas
        if self._is_victory_state():
            return 'win'
        
        # Verificar si no se puede continuar jugando
        if self.current_card:
            destination = self.get_card_destination(self.current_card)
            if destination and not self.piles_hidden[destination]:
                return 'loss'  # No hay más cartas para revelar en el destino
        
        return 'ongoing'

    def _is_victory_state(self):
        """Función de ayuda para comprobar la condición de victoria."""
        # Victoria: todas las cartas están reveladas (no hay cartas 'back' visibles)
        # y todas las cartas ocultas han sido reveladas
        all_revealed = all(card != 'back' for card in self.piles_visible.values())
        no_hidden_cards = all(len(pile) == 0 for pile in self.piles_hidden.values())
        
        return all_revealed and no_hidden_cards

    def get_board_state(self):
        """Devuelve una representación del estado del tablero para la Vista."""
        return {
            'visible': self.piles_visible,
            'hidden_counts': {i: len(self.piles_hidden[i]) for i in range(1, 14)},
            'current_card': self.current_card,
            'selected': self.selected_card_info if self.selected_card_info else None
        }