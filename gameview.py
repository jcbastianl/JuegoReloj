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
        self.revealed_card = None  # Para mostrar la carta recién revelada
        self.revealed_pile = None  # En qué montón se reveló la carta

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
        pending_reveal = board_state.get('pending_reveal')

        for i in range(1, 14):
            x, y = self.pile_positions[i]
            
            # Resaltar el montón donde se debe hacer clic para revelar
            if pending_reveal == i:
                self.canvas.create_rectangle(
                    x - 8, y - 8, 
                    x + ANCHO_CARTA + 8, y + ALTO_CARTA + 8,
                    fill="", outline="lime", width=5, tags="monton"
                )
                # Agregar texto indicativo
                self.canvas.create_text(
                    x + ANCHO_CARTA / 2, y - 25,
                    text="CLICK AQUÍ", fill="lime", 
                    font=("Arial", 10, "bold"), tags="monton"
                )
            
            # Resaltar el destino correcto cuando hay carta actual
            elif current_card and self.get_card_destination(current_card) == i:
                self.canvas.create_rectangle(
                    x - 6, y - 6, 
                    x + ANCHO_CARTA + 6, y + ALTO_CARTA + 6,
                    fill="", outline="orange", width=3, tags="monton"
                )
                # Agregar texto indicativo
                self.canvas.create_text(
                    x + ANCHO_CARTA / 2, y - 25,
                    text="DESTINO", fill="orange", 
                    font=("Arial", 9, "bold"), tags="monton"
                )
            
            # 1. Dibujar el efecto de montón con cartas ocultas (más visible)
            if hidden_counts[i] > 0:
                # Dibujar varias capas para efecto de montón
                for j in range(min(hidden_counts[i], 5)):
                     self.canvas.create_image(
                        x - j * OFFSET_MONTON_X, y - j * OFFSET_MONTON_Y,
                        image=self.assets.get_image('back'), anchor='nw', tags="monton"
                    )
                
                # Agregar número de cartas en el montón
                if hidden_counts[i] > 1:
                    self.canvas.create_text(
                        x + ANCHO_CARTA - 10, y + 10,
                        text=str(hidden_counts[i]), fill="yellow", 
                        font=("Arial", 10, "bold"), tags="monton"
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

        # 4. Mostrar carta revelada en su posición original (no en el centro)
        if self.revealed_card and self.revealed_pile:
            pile_x, pile_y = self.pile_positions[self.revealed_pile]
            
            # Dibujar un borde brillante alrededor del montón donde se reveló
            self.canvas.create_rectangle(
                pile_x - 5, pile_y - 5, 
                pile_x + ANCHO_CARTA + 5, pile_y + ALTO_CARTA + 5,
                fill="", outline="yellow", width=4, tags="revealed"
            )
            
            # Mostrar la carta revelada ligeramente desplazada para que se vea
            offset_x = -15
            offset_y = -15
            
            # Fondo para la carta revelada
            self.canvas.create_rectangle(
                pile_x + offset_x - 2, pile_y + offset_y - 2, 
                pile_x + offset_x + ANCHO_CARTA + 2, pile_y + offset_y + ALTO_CARTA + 2,
                fill="yellow", outline="orange", width=2, tags="revealed"
            )
            
            # La carta revelada
            img = self.assets.get_image(self.revealed_card)
            if img:
                self.canvas.create_image(pile_x + offset_x, pile_y + offset_y, image=img, anchor='nw', tags="revealed")
                
            # Texto indicativo
            destination = self.get_card_destination(self.revealed_card)
            self.canvas.create_text(
                pile_x + offset_x + ANCHO_CARTA / 2, pile_y + offset_y + ALTO_CARTA + 15,
                text=f"→ Montón {destination}", fill="white", 
                font=("Arial", 10, "bold"), tags="revealed"
            )

        # 5. Actualizar el texto de la carta actual
        if current_card:
             destination = self.get_card_destination(current_card)
             self.current_card_label.config(text=f"Carta Actual: {current_card} → Montón {destination}")
        else:
             self.current_card_label.config(text="No hay carta actual")

    def show_revealed_card(self, card, pile):
        """Muestra una carta recién revelada en su montón original"""
        self.revealed_card = card
        self.revealed_pile = pile
        self.canvas.delete("revealed")
        self.draw_board(self.controller.model.get_board_state())
    
    def hide_revealed_card(self):
        """Oculta la carta revelada"""
        self.revealed_card = None
        self.revealed_pile = None
        self.canvas.delete("revealed")
    
    def animate_card_move(self, card, from_pile, to_pile, callback=None):
        """Anima el movimiento de una carta de un montón a otro"""
        if self.animation_running:
            return
            
        self.animation_running = True
        from_x, from_y = self.pile_positions[from_pile]
        to_x, to_y = self.pile_positions[to_pile]
        
        # Crear carta animada
        img = self.assets.get_image(card)
        if img:
            animated_card = self.canvas.create_image(from_x, from_y, image=img, anchor='nw', tags="animated")
            
            # Calcular pasos de animación
            steps = 20
            dx = (to_x - from_x) / steps
            dy = (to_y - from_y) / steps
            
            def move_step(step):
                if step <= steps:
                    self.canvas.move(animated_card, dx, dy)
                    self.parent.after(30, lambda: move_step(step + 1))
                else:
                    self.canvas.delete(animated_card)
                    self.animation_running = False
                    if callback:
                        callback()
            
            move_step(0)

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