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

        # Si hay una revelación pendiente, solo aceptar clic en el montón correcto
        if self.model.pending_reveal:
            if pile_index == self.model.pending_reveal:
                revealed_card = self.model.try_reveal_from_pile(pile_index)
                if revealed_card:
                    self.view.show_revealed_card(revealed_card, pile_index)
                    self.view.show_status_message(f"Nueva carta revelada: {revealed_card}. Haz clic en el montón correcto para moverla.")
                else:
                    self.model.is_game_over = True
                    self.parent.after(1000, self.check_game_over)
                self.update_view()
            else:
                self.view.show_status_message(f"Debes hacer clic en el montón {self.model.pending_reveal} para revelar la siguiente carta.")
            return

        # Lógica normal de movimiento
        success, message = self.model.manual_play_step(clicked_pile)
        self.view.show_status_message(message)

        if success:
            # Ocultar carta revelada anterior y actualizar
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

    def shuffle_cards(self):
        """Baraja las cartas - solo permitido cuando no hay juego activo"""
        # Verificar si hay un juego en progreso
        if hasattr(self.model, 'game_mode') and self.model.game_mode and not self.model.is_game_over:
            self.view.show_status_message("❌ No puedes barajar durante un juego activo. Termina el juego primero.")
            return
        
        # Mostrar mensaje de barajado
        self.view.show_status_message("🎲 Barajando cartas...")
        
        # Baraja directamente
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
        self.view.show_status_message("¡Cartas barajadas! Orden mostrado en consola. Selecciona un modo de juego.")

    def _get_pile_name(self, pile_num):
        """Convierte número de montón a nombre de reloj"""
        clock_names = {
            1: "1 (As)", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
            7: "7", 8: "8", 9: "9", 10: "10", 11: "J (Jack)",
            12: "Q (Queen)", 13: "K (Rey)"
        }
        return clock_names.get(pile_num, str(pile_num))
    
    def quit_game(self):
        """Cierra la aplicación"""
        self.parent.quit()
        self.parent.destroy()
    
    def end_current_game(self):
        """Termina el juego actual y vuelve al menú"""
        if hasattr(self.model, 'game_mode') and self.model.game_mode and not self.model.is_game_over:
            self.model.is_game_over = True
            self.model.game_mode = None
            self.view.show_status_message("🔴 Juego terminado por el usuario.")
            self.parent.after(1000, self.show_main_menu)  # Esperar un poco antes de mostrar el menú
        else:
            self.show_main_menu()