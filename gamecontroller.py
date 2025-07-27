# controller.py
from gamemodel import GameModel
from gameview import GameView
from assets import AssetManager

class GameController:
    def __init__(self, parent):
        self.parent = parent
        self.model = GameModel()
        self.assets = AssetManager() # Cargar assets una vez
        self.view = GameView(parent, self, self.assets)
        self.view.pack(fill="both", expand=True)
        self.show_main_menu()

    def show_main_menu(self):
        self.view.display_menu()

    def start_new_game(self, mode):
        self.model.game_mode = mode
        self.model.shuffle_and_deal()
        self.update_view()
        self.view.show_status_message(f"Modo {mode.capitalize()} iniciado.")
        
        if mode == 'auto':
            # Iniciar el bucle automático
            self.parent.after(1000, self.run_auto_turn)

    def handle_pile_click(self, pile_index):
        if self.model.is_game_over or self.model.game_mode != 'manual':
            return
        
        # En modo manual, el jugador hace clic para mover la carta actual
        if self.model.current_card and self.model.current_card != 'back':
            expected_destination = self.model.get_card_destination(self.model.current_card)
            
            if pile_index == expected_destination:
                # Movimiento correcto
                success, message = self.model.make_move(self.model.current_card)
                self.view.show_status_message(message)
                
                if not success:
                    self.model.is_game_over = True
            else:
                # Movimiento incorrecto
                self.view.show_status_message(f"Incorrecto: {self.model.current_card} debe ir a la posición {expected_destination}")
        else:
            self.view.show_status_message("No hay carta actual para mover")
        
        self.update_view()
        self.check_for_game_over()

    def run_auto_turn(self):
        if self.model.is_game_over:
            return
        
        # En modo automático, simplemente ejecuta el siguiente movimiento
        if self.model.current_card:
            success, message = self.model.auto_play_step()
            self.view.show_status_message(message)
            
            if not success:
                self.model.is_game_over = True
        else:
            self.view.show_status_message("No hay carta actual para jugar")
            self.model.is_game_over = True
        
        self.update_view()
        if not self.check_for_game_over() and not self.model.is_game_over:
            self.parent.after(1200, self.run_auto_turn)

    def update_view(self):
        board_state = self.model.get_board_state()
        self.view.draw_board(board_state)

    def check_for_game_over(self):
        status = self.model.check_win_loss_condition()
        if status != 'ongoing':
            self.model.is_game_over = True
            if status == 'win':
                message = "¡GANASTE! Todas las cartas han sido reveladas."
            else:  # status == 'loss'
                message = "¡Perdiste! Salieron 4 Reyes o no hay más movimientos posibles."
            
            self.view.show_status_message(message)
            self.view.show_game_over_message("Juego Terminado", message)
            self.parent.after(2000, self.show_main_menu)
            return True
        return False