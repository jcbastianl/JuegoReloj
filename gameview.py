# gameview.py
import tkinter as tk
from tkinter import messagebox
import math

ANCHO_CARTA, ALTO_CARTA = 75, 110
ANCHO_CANVAS, ALTO_CANVAS = 800, 700
OFFSET_MONTON_X = 1
OFFSET_MONTON_Y = 1

class GameView(tk.Frame):
    def __init__(self, parent, controller, asset_manager):
        super().__init__(parent, bg="darkgreen")
        self.parent = parent
        self.controller = controller
        self.assets = asset_manager 
        self.pile_positions = self._calculate_positions()

        self.canvas = tk.Canvas(self, bg="darkgreen", width=ANCHO_CANVAS, height=ALTO_CANVAS, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(self, text="", bg="darkgreen", fg="white", font=("Arial", 14))
        self.canvas.create_window(ANCHO_CANVAS / 2, 20, window=self.status_label)
        
        self.current_card_label = tk.Label(self, text="", bg="darkgreen", fg="yellow", font=("Arial", 12, "bold"))
        self.canvas.create_window(ANCHO_CANVAS / 2, ALTO_CANVAS - 20, window=self.current_card_label)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        pile_index = self._identify_pile(event.x, event.y)
        if pile_index:
            self.controller.handle_pile_click(pile_index)

    def draw_board(self, board_state):
        self.canvas.delete("monton")
        
        visible_piles = board_state['visible']
        hidden_counts = board_state['hidden_counts']
        current_card = board_state.get('current_card')

        for i in range(1, 14):
            x, y = self.pile_positions[i]
            
            # 1. Dibujar el efecto de montón con cartas ocultas (solo si hay cartas ocultas)
            if hidden_counts[i] > 0:
                for j in range(min(hidden_counts[i], 4)):
                     self.canvas.create_image(
                        x - j * OFFSET_MONTON_X, y - j * OFFSET_MONTON_Y,
                        image=self.assets.get_image('back'), anchor='nw', tags="monton"
                    )

            # 2. Dibujar la carta visible (solo si hay una carta visible)
            card_name = visible_piles[i]
            if card_name != 'back':
                # Hay una carta visible en esta posición
                img = self.assets.get_image(card_name)
                if img:
                    self.canvas.create_image(x, y, image=img, anchor='nw', tags=("monton", f"monton_{i}"))
            elif hidden_counts[i] == 0:
                # No hay cartas ocultas ni visibles - mostrar espacio vacío
                self.canvas.create_rectangle(
                    x, y, x + ANCHO_CARTA, y + ALTO_CARTA,
                    fill="darkgreen", outline="gray", dash=(5, 5), tags="monton"
                )

            # 3. Dibujar el número del montón
            self.canvas.create_text(
                x + ANCHO_CARTA / 2, y - 15,
                text=str(i), fill="white", font=("Arial", 12, "bold"), tags="monton"
            )

        # 4. Actualizar el texto de la carta actual
        if current_card:
             destination = self.get_card_destination(current_card)
             self.current_card_label.config(text=f"Carta Actual: {current_card} → Montón {destination}")
        else:
             self.current_card_label.config(text="No hay carta actual")

    def get_card_destination(self, card):
        """Método auxiliar para obtener el destino de una carta"""
        if not card:
            return None
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
        # Recrear labels
        self.status_label = tk.Label(self, text="Solitario Reloj", bg="darkgreen", fg="yellow", font=("Arial", 18, "bold"))
        self.canvas.create_window(ANCHO_CANVAS / 2, 40, window=self.status_label)

        btn_auto = tk.Button(self.canvas, text="Modo Automático", command=lambda: self.controller.start_new_game('auto'), bg="#AED6F1", font=("Arial", 12), width=15)
        btn_manual = tk.Button(self.canvas, text="Modo Manual", command=lambda: self.controller.start_new_game('manual'), bg="#A9DFBF", font=("Arial", 12), width=15)
        
        self.canvas.create_window(ANCHO_CANVAS / 2, 120, window=btn_auto)
        self.canvas.create_window(ANCHO_CANVAS / 2, 160, window=btn_manual)

    def _calculate_positions(self):
        positions = {}
        center_x = ANCHO_CANVAS / 2
        center_y = ALTO_CANVAS / 2
        radius = 250

        # Posiciones para 1-12 en forma de reloj
        for i in range(1, 13):
            # El ángulo se ajusta para que el 12 esté arriba, el 3 a la derecha, etc.
            angle = math.radians(-60 + (i * 30))
            x = center_x + radius * math.cos(angle) - (ANCHO_CARTA / 2)
            y = center_y + radius * math.sin(angle) - (ALTO_CARTA / 2)
            positions[i] = (x, y)
        
        # Posición 13 en el centro
        positions[13] = (center_x - ANCHO_CARTA / 2, center_y - ALTO_CARTA / 2)
        return positions

    def _identify_pile(self, x, y):
        for pile_index, (px, py) in self.pile_positions.items():
            if (px <= x <= px + ANCHO_CARTA and 
                py <= y <= py + ALTO_CARTA):
                return pile_index
        return None