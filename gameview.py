# gameview.py
import tkinter as tk
from tkinter import messagebox
import math
import random

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
        self.canvas.create_window(ANCHO_CANVAS / 2, 20, window=self.status_label)

        self.current_card_label = tk.Label(self, text="", bg="darkgreen", fg="yellow", font=("Arial", 12, "bold"))
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.current_card_label)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        if self.animation_running: return # No hacer nada si hay una animación en curso
        pile_index = self._identify_pile(event.x, event.y)
        if pile_index:
            self.controller.handle_pile_click(pile_index)

    def draw_board(self, board_state):
        self.canvas.delete("monton")
        self.canvas.delete("game_buttons")  # Eliminar botones de juego anteriores

        visible_piles = board_state['visible']
        hidden_counts = board_state['hidden_counts']
        current_card = board_state.get('current_card')
        pending_reveal = board_state.get('pending_reveal')

        # Agregar botones durante el juego
        btn_menu = tk.Button(self.canvas, text="🏠 Menú", command=self.controller.show_main_menu, bg="#4ECDC4", fg="white", font=("Arial", 10), width=10)
        btn_fin = tk.Button(self.canvas, text="🔴 Terminar", command=self.controller.end_current_game, bg="#FF6B6B", fg="white", font=("Arial", 10), width=10)
        
        self.canvas.create_window(ANCHO_CANVAS - 70, 50, window=btn_menu, tags="game_buttons")
        self.canvas.create_window(ANCHO_CANVAS - 70, 90, window=btn_fin, tags="game_buttons")

        for i in range(1, 14):
            x, y = self.pile_positions[i]

            if pending_reveal == i:
                self.canvas.create_rectangle(
                    x - 8, y - 8, x + ANCHO_CARTA + 8, y + ALTO_CARTA + 8,
                    fill="", outline="lime", width=5, tags="monton"
                )
            elif current_card and self.get_card_destination(current_card) == i:
                self.canvas.create_rectangle(
                    x - 6, y - 6, x + ANCHO_CARTA + 6, y + ALTO_CARTA + 6,
                    fill="", outline="orange", width=3, tags="monton"
                )

            if hidden_counts[i] > 0:
                for j in range(min(hidden_counts[i], 5)):
                     self.canvas.create_image(
                        x - j * OFFSET_MONTON_X, y - j * OFFSET_MONTON_Y,
                        image=self.assets.get_image('back'), anchor='nw', tags="monton"
                    )
                if hidden_counts[i] > 1:
                    self.canvas.create_text(
                        x + ANCHO_CARTA - 10, y + 10, text=str(hidden_counts[i]),
                        fill="yellow", font=("Arial", 10, "bold"), tags="monton"
                    )

            card_name = visible_piles[i]
            if card_name != 'back':
                img = self.assets.get_image(card_name)
                if img:
                    self.canvas.create_image(x, y, image=img, anchor='nw', tags=("monton", f"monton_{i}"))
            elif hidden_counts[i] == 0:
                self.canvas.create_rectangle(
                    x, y, x + ANCHO_CARTA, y + ALTO_CARTA,
                    fill="darkgreen", outline="gray", dash=(5, 5), tags="monton"
                )
            self.canvas.create_text(
                x + ANCHO_CARTA / 2, y - 15, text=str(i), fill="white",
                font=("Arial", 12, "bold"), tags="monton"
            )

        if self.revealed_card and self.revealed_pile:
            self.draw_revealed_card_display()

        if current_card:
             destination = self.get_card_destination(current_card)
             self.current_card_label.config(text=f"Carta Actual: {current_card} → Montón {destination}")
        else:
             self.current_card_label.config(text="No hay carta actual")

    def draw_revealed_card_display(self):
        pile_x, pile_y = self.pile_positions[self.revealed_pile]
        offset_x, offset_y = -15, -15
        self.canvas.create_rectangle(
            pile_x - 5, pile_y - 5, pile_x + ANCHO_CARTA + 5, pile_y + ALTO_CARTA + 5,
            fill="", outline="yellow", width=4, tags="revealed"
        )
        img = self.assets.get_image(self.revealed_card)
        if img:
            self.canvas.create_image(pile_x + offset_x, pile_y + offset_y, image=img, anchor='nw', tags="revealed")
        destination = self.get_card_destination(self.revealed_card)
        self.canvas.create_text(
            pile_x + offset_x + ANCHO_CARTA / 2, pile_y + offset_y + ALTO_CARTA + 15,
            text=f"→ Montón {destination}", fill="white", font=("Arial", 10, "bold"), tags="revealed"
        )

    def show_revealed_card(self, card, pile):
        self.revealed_card = card
        self.revealed_pile = pile
        self.canvas.delete("revealed")
        self.draw_board(self.controller.model.get_board_state())

    def hide_revealed_card(self):
        self.revealed_card = None
        self.revealed_pile = None
        self.canvas.delete("revealed")

    def animate_card_move(self, card, from_pile, to_pile, callback=None):
        if self.animation_running:
            if callback: callback()
            return

        self.animation_running = True
        from_x, from_y = self.pile_positions[from_pile]
        to_x, to_y = self.pile_positions[to_pile]
        img = self.assets.get_image(card)

        if img:
            animated_card = self.canvas.create_image(from_x, from_y, image=img, anchor='nw', tags="animated")
            steps = 20
            dx = (to_x - from_x) / steps
            dy = (to_y - from_y) / steps

            def move_step(step):
                if step <= steps:
                    self.canvas.move(animated_card, dx, dy)
                    self.parent.after(20, lambda: move_step(step + 1))
                else:
                    self.canvas.delete(animated_card)
                    self.animation_running = False
                    if callback:
                        callback()
            move_step(0)

    def animate_shuffle(self, callback=None):
        """Animación de barajado simple y fácil de explicar."""
        if self.animation_running:
            return
        
        self.animation_running = True
        self.canvas.delete("all")
        self.display_menu()
        self.show_status_message("🎲 Barajando cartas...")

        # 1. Crear un mazo de cartas de animación en el centro
        deck_x, deck_y = ANCHO_CANVAS / 2, ALTO_CANVAS / 2
        cards = []
        for i in range(15):
            card = self.canvas.create_image(deck_x, deck_y, image=self.assets.get_image('back'), anchor='center')
            cards.append(card)

        # 2. Mover las cartas en un arco simple
        def move_cards(step):
            if step > 100:  # Fin de la animación
                self.canvas.delete("all") # Limpiar las cartas de animación
                self.animation_running = False
                if callback:
                    callback()
                return

            for i, card in enumerate(cards):
                # Calcular un movimiento en forma de arco (usando seno)
                offset_x = 150 * math.sin(math.radians(step * 3.6 + i * 24))
                self.canvas.moveto(card, deck_x + offset_x - (ANCHO_CARTA/2), deck_y - (ALTO_CARTA/2))
            
            self.parent.after(15, lambda: move_cards(step + 1))

        move_cards(0) # Empezar la animación

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

    def show_game_over_message(self, title, message):
        messagebox.showinfo(title, message)
        self.controller.show_main_menu()

    def display_menu(self):
        self.canvas.delete("all")
        
        # Recrear los labels porque se eliminaron con delete("all")
        self.status_label = tk.Label(self, text="🎴 Solitario Reloj 🎴", bg="darkgreen", fg="yellow", font=("Arial", 18, "bold"))
        self.canvas.create_window(ANCHO_CANVAS / 2, 40, window=self.status_label)
        
        self.current_card_label = tk.Label(self, text="Selecciona un modo de juego para comenzar", bg="darkgreen", fg="white", font=("Arial", 12))
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.current_card_label)

        # Botones principales centrados
        btn_auto = tk.Button(self.canvas, text="🤖 Modo Automático", command=lambda: self.controller.start_new_game('auto'), bg="#AED6F1", font=("Arial", 12), width=20, height=2)
        btn_manual = tk.Button(self.canvas, text="🎮 Modo Manual", command=lambda: self.controller.start_new_game('manual'), bg="#A9DFBF", font=("Arial", 12), width=20, height=2)
        
        # Botones secundarios en el lateral derecho
        btn_shuffle = tk.Button(self.canvas, text="🎲 Barajar", command=self.controller.shuffle_cards, bg="#F7DC6F", font=("Arial", 10), width=12)
        btn_fin = tk.Button(self.canvas, text="❌ Salir", command=self.controller.quit_game, bg="#FF6B6B", fg="white", font=("Arial", 10), width=12)

        # Posicionar botones principales en el centro
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2 - 50, window=btn_auto)
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS / 2, window=btn_manual)
        
        # Posicionar botones secundarios en el lateral derecho
        self.canvas.create_window(ANCHO_CANVAS - 80, 80, window=btn_shuffle)
        self.canvas.create_window(ANCHO_CANVAS - 80, 120, window=btn_fin)

    def _calculate_positions(self):
        positions = {}
        center_x, center_y, radius = ANCHO_CANVAS / 2, ALTO_CANVAS / 2, 250
        for i in range(1, 13):
            angle = math.radians(-60 + (i * 30))
            x = center_x + radius * math.cos(angle) - (ANCHO_CARTA / 2)
            y = center_y + radius * math.sin(angle) - (ALTO_CARTA / 2)
            positions[i] = (x, y)
        positions[13] = (center_x - ANCHO_CARTA / 2, center_y - ALTO_CARTA / 2)
        return positions

    def _identify_pile(self, x, y):
        for i, (px, py) in self.pile_positions.items():
            if px <= x <= px + ANCHO_CARTA and py <= y <= py + ALTO_CARTA:
                return i
        return None