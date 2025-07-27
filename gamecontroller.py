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
        self.model.is_game_over = True
        self.model.game_mode = None
        self.view.display_menu()

    def start_new_game(self, mode):
        """
        Esta función ahora se asegura de que la lógica y el dibujado
        ocurran en el orden correcto, evitando la pantalla verde.
        """
        # 1. Configurar la lógica del juego en el modelo
        self.model.game_mode = mode
        self.model.shuffle_and_deal()
        
        # 2. Forzar la actualización de la vista para dibujar el tablero
        self.update_view()

        # 3. Iniciar el modo de juego correspondiente
        if mode == 'auto':
            self.view.show_status_message("Modo Automático iniciado. Observa cómo se juega.")
            self.parent.after(1000, self.run_auto_turn)
        else:
            self.view.show_status_message("Modo Manual iniciado. Haz clic en el montón correcto.")

    def handle_pile_click(self, pile_index):
        if self.model.is_game_over or self.model.game_mode != 'manual':
            return

        if self.model.pending_reveal:
            if pile_index == self.model.pending_reveal:
                revealed_card = self.model.try_reveal_from_pile(pile_index)
                if revealed_card:
                    self.view.show_revealed_card(revealed_card, pile_index)
                    self.view.show_status_message(f"Nueva carta revelada: {revealed_card}. ¡A jugar!")
                else:
                    self.model.is_game_over = True
                    self.parent.after(500, self.check_game_over)
                self.update_view()
            else:
                self.view.show_status_message(f"Debes hacer clic en el montón {self.model.pending_reveal} para revelar.")
            return

        success, message = self.model.manual_play_step(pile_index)
        self.view.show_status_message(message)

        if success:
            self.view.hide_revealed_card()
            self.update_view()

        if self.model.is_game_over:
            self.parent.after(500, self.check_game_over)

    def run_auto_turn(self):
        if self.model.is_game_over or not self.model.current_card:
            self.check_game_over()
            return

        card_to_move = self.model.current_card
        destination = self.model.get_card_destination(card_to_move)
        source_pile = self.model.last_move_from if self.model.last_move_from is not None else 13
        
        success, message = self.model.auto_play_step()

        def after_animation():
            self.view.show_status_message(message)
            self.update_view()
            if not self.model.is_game_over:
                self.parent.after(800, self.run_auto_turn)
            else:
                self.parent.after(500, self.check_game_over)

        self.view.animate_card_move(card_to_move, source_pile, destination, after_animation)

    def update_view(self):
        board_state = self.model.get_board_state()
        self.view.draw_board(board_state)
        # Actualizar también la información de la carta actual
        current_card = board_state.get('current_card')
        self.view.update_status_labels(current_card)

    def check_game_over(self):
        if self.model.is_game_over:
            status = self.model.check_game_status()
            if status == 'win':
                message = "¡GANASTE! Todas las cartas están en su lugar correcto."
            else:
                message = "¡Perdiste! Salieron los 4 Reyes antes de tiempo."
            
            self.view.show_game_over_message("Juego Terminado", message)
            return True
        return False
    
    def shuffle_cards(self):
        """Baraja las cartas con animación - solo permitido cuando no hay juego activo"""
        # Verificar si hay un juego en progreso
        if hasattr(self.model, 'game_mode') and self.model.game_mode and not self.model.is_game_over:
            self.view.show_status_message("❌ No puedes barajar durante un juego activo. Termina el juego primero.")
            return
        
        # Mostrar mensaje de barajado
        self.view.show_status_message("🎲 Barajando cartas...")
        
        # Definir qué hacer después de la animación
        def after_shuffle_animation():
            try:
                # Baraja las cartas en el modelo
                self.model.shuffle_and_deal()
                
                # Imprimir orden de las cartas en consola
                print("\n" + "="*50)
                print("🎴 NUEVO ORDEN DE CARTAS DESPUÉS DEL BARAJADO:")
                print("="*50)
                
                for pile_num in range(1, 14):
                    cards_in_pile = self.model.piles_hidden[pile_num]
                    pile_name = self._get_pile_name(pile_num)
                    print(f"Montón {pile_num:2d} ({pile_name:>11}): {cards_in_pile}")
                
                print("="*50)
                print(f"Total de cartas: {sum(len(pile) for pile in self.model.piles_hidden.values())}")
                print("="*50 + "\n")
                
                # Volver al menú principal después de barajar
                self.show_main_menu()
                self.view.show_status_message("¡Cartas barajadas! Selecciona un modo de juego.")
                
            except Exception as e:
                print(f"Error en after_shuffle_animation: {e}")
                # Si hay error, al menos volver al menú
                self.show_main_menu()
        
        # Iniciar la animación de barajado con callback
        self.view.animate_shuffle(callback=after_shuffle_animation)

    def end_current_game(self):
        self.model.is_game_over = True
        self.model.game_mode = None
        self.view.show_status_message("Juego terminado. ¡Vuelve a intentarlo!")
        self.parent.after(500, self.show_main_menu)

    def quit_game(self):
        self.parent.destroy()
    
    def _get_pile_name(self, pile_num):
        """Convierte número de montón a nombre de reloj"""
        clock_names = {
            1: "1 (As)", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
            7: "7", 8: "8", 9: "9", 10: "10", 11: "J (Jack)",
            12: "Q (Queen)", 13: "K (Rey)"
        }
        return clock_names.get(pile_num, str(pile_num))