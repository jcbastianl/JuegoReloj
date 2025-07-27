# gamecontroller.py
from gamemodel import GameModel
from gameview import GameView
from assets import AssetManager

class GameController:
    def __init__(self, parent):
        self.parent = parent
        self.model = GameModel()
        self.assets = AssetManager()
        self.view = GameView(parent, self, self.assets)
        self.view.pack(fill="both", expand=True)
        self.show_main_menu()

    def show_main_menu(self):
        self.view.display_menu()

    def start_new_game(self, mode):
        self.model.game_mode = mode
        self.model.shuffle_and_deal()
        self.update_view()
        
        if mode == 'auto':
            self.view.show_status_message("Modo Automático iniciado. Observa cómo se juega.")
            self.parent.after(1000, self.run_auto_turn)  # Dar tiempo para ver el estado inicial
        else:
            self.view.show_status_message("Modo Manual iniciado. Haz clic en el montón correcto.")
            
    def handle_pile_click(self, pile_index):
        if self.model.is_game_over or self.model.game_mode != 'manual':
            return
        
        # Si hay una revelación pendiente, cualquier clic la completa
        if self.model.pending_reveal:
            revealed_card = self.model.complete_manual_move()
            if revealed_card:
                self.view.show_revealed_card(revealed_card)
                self.view.show_status_message(f"Nueva carta revelada: {revealed_card}. Haz clic en el montón correcto.")
            else:
                self.model.is_game_over = True
                self.parent.after(1000, self.check_game_over)
            self.update_view()
            return
        
        # Lógica normal de movimiento
        success, message = self.model.manual_play_step(pile_index)
        self.view.show_status_message(message)
        
        if success:
            # Ocultar carta revelada y actualizar
            self.view.hide_revealed_card()
            self.update_view()
        
        if self.model.is_game_over:
            self.parent.after(1000, self.check_game_over)
            
    def run_auto_turn(self):
        if self.model.is_game_over:
            self.check_game_over()
            return
        
        if not self.model.current_card:
            self.check_game_over()
            return
            
        # Obtener información del movimiento antes de ejecutarlo
        card_to_move = self.model.current_card
        destination = self.model.get_card_destination(card_to_move)
        
        # Determinar de dónde viene la carta (centro si es la primera, o del último montón)
        source_pile = self.model.last_move_from if self.model.last_move_from else 13
        
        # Ejecutar el movimiento
        success, message = self.model.auto_play_step()
        
        # Animar el movimiento
        def after_animation():
            self.view.show_status_message(message)
            self.update_view()
            if not self.model.is_game_over:
                self.parent.after(800, self.run_auto_turn)
            else:
                self.parent.after(1000, self.check_game_over)
        
        # Iniciar animación
        self.view.animate_card_move(card_to_move, source_pile, destination, after_animation)

    def update_view(self):
        board_state = self.model.get_board_state()
        self.view.draw_board(board_state)
        # El mensaje ya se maneja en los métodos individuales

    def check_game_over(self):
        status = self.model.check_game_status()
        if status != 'ongoing':
            self.model.is_game_over = True
            if status == 'win':
                message = "¡GANASTE! Todas las cartas están en su lugar correcto."
            else: 
                message = "¡Perdiste! Salieron 4 Reyes o no pudiste completar el juego."
            
            self.update_view()
            self.view.show_game_over_message("Juego Terminado", message)
            return True
        return False