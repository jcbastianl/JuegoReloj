# gameview.py
import tkinter as tk
from tkinter import messagebox
import math

ANCHO_CARTA, ALTO_CARTA = 75, 110
ANCHO_CANVAS, ALTO_CANVAS = 800, 700
OFFSET_MONTON_X = 3
OFFSET_MONTON_Y = 3

class GameView(tk.Frame):
    def __init__(self, parent, controller, asset_manager):
        super().__init__(parent, bg="darkgreen")
        self.parent = parent
        self.controller = controller
        self.assets = asset_manager
        self.pile_positions = self._calculate_positions()
        self.animation_running = False
        self.revealed_card = None
        self.revealed_pile = None

        self.canvas = tk.Canvas(self, bg="darkgreen", width=ANCHO_CANVAS, height=ALTO_CANVAS, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(self, text="", bg="darkgreen", fg="white", font=("Arial", 14))
        self.current_card_label = tk.Label(self, text="", bg="darkgreen", fg="yellow", font=("Arial", 12, "bold"))
        
        self.canvas.create_window(ANCHO_CANVAS / 2, 20, window=self.status_label)
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.current_card_label)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        if self.animation_running: return
        pile_index = self._identify_pile(event.x, event.y)
        if pile_index:
            self.controller.handle_pile_click(pile_index)

    def draw_board(self, board_state):
        # Eliminar TODOS los elementos excepto los labels permanentes
        self.canvas.delete("monton", "game_buttons", "revealed", "menu_buttons")
        
        visible_piles, hidden_counts = board_state['visible'], board_state['hidden_counts']
        current_card, pending_reveal = board_state.get('current_card'), board_state.get('pending_reveal')

        # Botón de menú durante el juego
        btn_menu = tk.Button(self, text="🏠 Menú Principal", command=self.controller.end_current_game, bg="#4ECDC4", fg="black", font=("Arial", 9))
        self.canvas.create_window(ANCHO_CANVAS - 80, 40, window=btn_menu, tags="game_buttons")

        for i in range(1, 14):
            x, y = self.pile_positions[i]
            if pending_reveal == i:
                self.canvas.create_rectangle(x - 8, y - 8, x + ANCHO_CARTA + 8, y + ALTO_CARTA + 8, fill="", outline="lime", width=5)
            elif current_card and self.get_card_destination(current_card) == i:
                self.canvas.create_rectangle(x - 6, y - 6, x + ANCHO_CARTA + 6, y + ALTO_CARTA + 6, fill="", outline="orange", width=3)

            if hidden_counts.get(i, 0) > 0:
                for j in range(min(hidden_counts[i], 5)):
                     self.canvas.create_image(x - j * OFFSET_MONTON_X, y - j * OFFSET_MONTON_Y, image=self.assets.get_image('back'), anchor='nw')
                if hidden_counts[i] > 1:
                    self.canvas.create_text(x + ANCHO_CARTA - 10, y + 10, text=str(hidden_counts[i]), fill="yellow", font=("Arial", 10, "bold"))

            card_name = visible_piles.get(i, 'back')
            if card_name != 'back':
                img = self.assets.get_image(card_name)
                if img: self.canvas.create_image(x, y, image=img, anchor='nw')
            elif hidden_counts.get(i, 0) == 0:
                self.canvas.create_rectangle(x, y, x + ANCHO_CARTA, y + ALTO_CARTA, fill="darkgreen", outline="gray", dash=(5, 5))
            
            self.canvas.create_text(x + ANCHO_CARTA / 2, y - 15, text=str(i), fill="white", font=("Arial", 12, "bold"))

        if self.revealed_card and self.revealed_pile: self.draw_revealed_card_display()
        self.update_status_labels(current_card)

    def draw_revealed_card_display(self):
        pile_x, pile_y = self.pile_positions[self.revealed_pile]
        offset_x, offset_y = -15, -15
        self.canvas.create_rectangle(pile_x - 5, pile_y - 5, pile_x + ANCHO_CARTA + 5, pile_y + ALTO_CARTA + 5, fill="", outline="yellow", width=4)
        img = self.assets.get_image(self.revealed_card)
        if img: self.canvas.create_image(pile_x + offset_x, pile_y + offset_y, image=img, anchor='nw')
        destination = self.get_card_destination(self.revealed_card)
        self.canvas.create_text(pile_x + offset_x + ANCHO_CARTA/2, pile_y + offset_y + ALTO_CARTA + 15, text=f"→ Montón {destination}", fill="white", font=("Arial", 10, "bold"))

    def show_revealed_card(self, card, pile):
        self.revealed_card, self.revealed_pile = card, pile
        self.draw_board(self.controller.model.get_board_state())

    def hide_revealed_card(self):
        self.revealed_card, self.revealed_pile = None, None

    def animate_card_move(self, card, from_pile, to_pile, callback=None):
        if self.animation_running:
            if callback: callback()
            return
        self.animation_running = True
        from_x, from_y = self.pile_positions.get(from_pile, (0,0))
        to_x, to_y = self.pile_positions.get(to_pile, (0,0))
        img = self.assets.get_image(card)
        if img:
            animated_card = self.canvas.create_image(from_x, from_y, image=img, anchor='nw')
            steps = 20
            dx, dy = (to_x - from_x) / steps, (to_y - from_y) / steps
            def move_step(step):
                if step < steps:
                    self.canvas.move(animated_card, dx, dy)
                    self.parent.after(20, lambda: move_step(step + 1))
                else:
                    self.canvas.delete(animated_card)
                    self.animation_running = False
                    if callback: callback()
            move_step(0)
        else:
            self.animation_running = False
            if callback: callback()

    def animate_shuffle(self, callback=None):
        """Animación simple de barajado"""
        if self.animation_running:
            if callback: 
                callback()
            return
            
        self.animation_running = True
        
        # Limpiar el canvas pero mantener los labels
        self.canvas.delete("all")
        self.canvas.create_window(ANCHO_CANVAS / 2, 20, window=self.status_label)
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.current_card_label)
        
        # Crear varias cartas que se van a mover
        center_x, center_y = ANCHO_CANVAS / 2, ALTO_CANVAS / 2
        cards = []
        
        # Crear 8 cartas en el centro
        for i in range(8):
            card_img = self.canvas.create_image(
                center_x + i * 2, center_y + i * 2, 
                image=self.assets.get_image('back'), 
                anchor='center', tags="shuffle_animation"
            )
            cards.append(card_img)
        
        step = 0
        def animate_step():
            nonlocal step
            if step > 40:  # Reducir tiempo de animación
                self.canvas.delete("shuffle_animation")
                self.animation_running = False
                # Asegurar que el callback se ejecute
                if callback:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Error en callback: {e}")
                        # Si hay error, al menos volver al menú
                        self.controller.show_main_menu()
                return
            
            # Mover las cartas en círculo
            for i, card in enumerate(cards):
                angle = math.radians(step * 9 + i * 45)  # Más rápido
                offset_x = 80 * math.cos(angle)
                offset_y = 80 * math.sin(angle)
                self.canvas.coords(card, center_x + offset_x, center_y + offset_y)
            
            step += 1
            self.parent.after(30, animate_step)  # Más rápido
        
        animate_step()

    def get_card_destination(self, card):
        if not card: return None
        value = card[:-1]
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        try: 
            return valores.index(value) + 1
        except ValueError: 
            return 13

    def show_status_message(self, message):
        self.status_label.config(text=message)

    def update_status_labels(self, current_card):
        if current_card:
            destination = self.get_card_destination(current_card)
            self.current_card_label.config(text=f"Carta Actual: {current_card} → Montón {destination}")
        else:
            self.current_card_label.config(text="No hay carta actual")

    def show_game_over_message(self, title, message):
        messagebox.showinfo(title, message)
        self.controller.show_main_menu()

    def display_menu(self):
        self.canvas.delete("all")
        self.status_label.config(text="🎴 Solitario Reloj 🎴")
        self.current_card_label.config(text="Selecciona un modo de juego para comenzar")
        self.canvas.create_window(ANCHO_CANVAS / 2, 40, window=self.status_label)
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.current_card_label)

        btn_auto = tk.Button(self, text="🤖 Modo Automático", command=lambda: self.controller.start_new_game('auto'), font=("Arial", 12), width=20, height=2)
        btn_manual = tk.Button(self, text="🎮 Modo Manual", command=lambda: self.controller.start_new_game('manual'), font=("Arial", 12), width=20, height=2)
        btn_shuffle = tk.Button(self, text="🎲 Barajar y Reiniciar", command=self.controller.shuffle_cards, font=("Arial", 12), width=20, height=2)
        btn_quit = tk.Button(self, text="❌ Salir del Juego", command=self.controller.quit_game, font=("Arial", 12), width=20, height=2)
        
        # Agregar tags a los botones del menú para poder eliminarlos
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 - 100, window=btn_auto, tags="menu_buttons")
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 - 30, window=btn_manual, tags="menu_buttons")
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 + 40, window=btn_shuffle, tags="menu_buttons")
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 + 110, window=btn_quit, tags="menu_buttons")

    def _calculate_positions(self):
        positions = {}
        center_x, center_y, radius = ANCHO_CANVAS / 2, ALTO_CANVAS / 2, 250
        for i in range(1, 13):
            angle = math.radians(-60 + (i * 30))
            x, y = center_x + radius * math.cos(angle) - (ANCHO_CARTA / 2), center_y + radius * math.sin(angle) - (ALTO_CARTA / 2)
            positions[i] = (x, y)
        positions[13] = (center_x - ANCHO_CARTA / 2, center_y - ALTO_CARTA / 2)
        return positions

    def _identify_pile(self, x, y):
        for i, (px, py) in self.pile_positions.items():
            if px <= x <= px + ANCHO_CARTA and py <= y <= py + ALTO_CARTA:
                return i
        return None