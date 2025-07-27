# view.py
import tkinter as tk
from tkinter import messagebox
import math

# Suponiendo que AssetManager es una clase que carga y provee imágenes
# from assets import AssetManager 

ANCHO_CARTA, ALTO_CARTA = 75, 110
ANCHO_CANVAS, ALTO_CANVAS = 800, 700
OFFSET_MONTON = 15

class GameView(tk.Frame):
    def __init__(self, parent, controller, asset_manager):
        super().__init__(parent)
        self.controller = controller
        self.assets = asset_manager # asset_manager.images
        self.pile_positions = self._calculate_positions()

        self.canvas = tk.Canvas(self, bg="darkgreen", width=ANCHO_CANVAS, height=ALTO_CANVAS)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(self, text="", bg="darkgreen", fg="white", font=("Arial", 14))
        self.canvas.create_window(ANCHO_CANVAS / 2, 20, window=self.status_label)

        self.bind_events()

    def bind_events(self):
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
        selected_index = board_state['selected'][0] if board_state['selected'] else None

        for i in range(1, 14):
            x, y = self.pile_positions[i]
            card_visible = visible_piles[i]
            num_ocultas = hidden_counts[i]

            # Dibujar montones ocultos
            for j in range(min(num_ocultas, 3)):  # Máximo 3 capas para visualización
                offset_x = j * 2
                offset_y = j * 2
                self.canvas.create_rectangle(
                    x + offset_x, y + offset_y, 
                    x + ANCHO_CARTA + offset_x, y + ALTO_CARTA + offset_y,
                    fill="navy", outline="white", tags="monton"
                )

            # Dibujar carta visible
            if card_visible == 'back':
                self.canvas.create_rectangle(
                    x, y, x + ANCHO_CARTA, y + ALTO_CARTA,
                    fill="blue", outline="white", tags="monton"
                )
                self.canvas.create_text(
                    x + ANCHO_CARTA//2, y + ALTO_CARTA//2,
                    text="?", fill="white", font=("Arial", 16), tags="monton"
                )
            else:
                # Determinar color de la carta
                if card_visible and len(card_visible) > 1:
                    suit = card_visible[-1]
                    color = "red" if suit in ['♥', '♦'] else "black"
                    bg_color = "white"
                    
                    # Resaltar la carta actual en juego
                    if card_visible == current_card:
                        bg_color = "lightyellow"
                        border_color = "orange"
                        border_width = 3
                    else:
                        border_color = "black"
                        border_width = 1
                else:
                    color = "black"
                    bg_color = "lightgray"
                    border_color = "black"
                    border_width = 1
                
                self.canvas.create_rectangle(
                    x, y, x + ANCHO_CARTA, y + ALTO_CARTA,
                    fill=bg_color, outline=border_color, width=border_width, tags="monton"
                )
                if card_visible and card_visible != 'back':
                    self.canvas.create_text(
                        x + ANCHO_CARTA//2, y + ALTO_CARTA//2,
                        text=card_visible, fill=color, font=("Arial", 12, "bold"), tags="monton"
                    )

            # Dibujar número del montón
            self.canvas.create_text(
                x + ANCHO_CARTA//2, y - 15,
                text=str(i), fill="white", font=("Arial", 12, "bold"), tags="monton"
            )

            # Dibujar contador de cartas ocultas
            if num_ocultas > 0:
                self.canvas.create_text(
                    x + ANCHO_CARTA - 10, y + 10,
                    text=str(num_ocultas), fill="yellow", font=("Arial", 10, "bold"), tags="monton"
                )

            # Dibuja un rectángulo de selección
            if selected_index == i:
                self.canvas.create_rectangle(
                    x - 3, y - 3, x + ANCHO_CARTA + 3, y + ALTO_CARTA + 3,
                    fill="", outline="yellow", width=3, tags="monton"
                )
        
        # Mostrar la carta actual en una esquina si existe
        if current_card and current_card != 'back':
            expected_dest = self._get_card_destination_for_display(current_card)
            status_text = f"Carta actual: {current_card} → Posición {expected_dest}"
            self.canvas.create_text(
                ANCHO_CANVAS - 200, ALTO_CANVAS - 30,
                text=status_text, fill="white", font=("Arial", 12, "bold"), tags="monton"
            )
    
    def show_status_message(self, message):
        """Muestra un mensaje en la etiqueta de estado"""
        self.status_label.config(text=message)
        print(f"Estado: {message}")  # También imprimir en consola para depuración

    def show_game_over_message(self, title, message):
        messagebox.showinfo(title, message)

    def display_menu(self):
        self.canvas.delete("all")
        # Recrear el label de estado
        self.status_label = tk.Label(self, text="Solitario Reloj - Selecciona un modo de juego", bg="darkgreen", fg="white", font=("Arial", 14))
        self.canvas.create_window(ANCHO_CANVAS / 2, 30, window=self.status_label)
        
        # Instrucciones del juego
        instructions = [
            "CÓMO JUGAR:",
            "• Se revela la primera carta del centro (pos. 13)",
            "• El valor de la carta determina a qué montón va:",
            "  As→1, 2→2, ..., J→11, Q→12, K→13",
            "• Al moverla se revela la siguiente carta",
            "• GANAS si todas las cartas se revelan",
            "• PIERDES si salen 4 Reyes antes"
        ]
        
        start_y = 80
        for i, instruction in enumerate(instructions):
            color = "yellow" if i == 0 else "white"
            font_size = 12 if i == 0 else 10
            self.canvas.create_text(
                ANCHO_CANVAS / 2, start_y + i * 20,
                text=instruction, fill=color, font=("Arial", font_size, "bold" if i == 0 else "normal")
            )
        
        btn_auto = tk.Button(self.canvas, text="Modo Automático", command=lambda: self.controller.start_new_game('auto'), bg="lightblue", font=("Arial", 12))
        btn_manual = tk.Button(self.canvas, text="Modo Manual", command=lambda: self.controller.start_new_game('manual'), bg="lightgreen", font=("Arial", 12))
        
        self.canvas.create_window(ANCHO_CANVAS / 2 - 100, 280, window=btn_auto)
        self.canvas.create_window(ANCHO_CANVAS / 2 + 100, 280, window=btn_manual)

    def _calculate_positions(self):
        # Lógica de cálculo de posiciones en forma de reloj
        positions = {}
        center_x = ANCHO_CANVAS // 2
        center_y = ALTO_CANVAS // 2
        radius = 200  # Radio del círculo
        
        # Posiciones para los números 1-12 en forma de reloj
        for i in range(1, 13):
            angle = (i - 3) * (2 * math.pi / 12)  # -3 para que 12 esté arriba
            x = center_x + radius * math.cos(angle) - ANCHO_CARTA // 2
            y = center_y + radius * math.sin(angle) - ALTO_CARTA // 2
            positions[i] = (int(x), int(y))
        
        # Posición 13 en el centro
        positions[13] = (center_x - ANCHO_CARTA // 2, center_y - ALTO_CARTA // 2)
        
        return positions

    def _identify_pile(self, x, y):
        # Lógica de identificación de montón
        for pile_index, (pile_x, pile_y) in self.pile_positions.items():
            if (pile_x <= x <= pile_x + ANCHO_CARTA and 
                pile_y <= y <= pile_y + ALTO_CARTA):
                return pile_index
        return None

    def _get_card_destination_for_display(self, card):
        """Método auxiliar para mostrar el destino de una carta"""
        if not card or card == 'back':
            return None
        
        value = card[:-1]  # Remover el palo
        
        # Mapeo de valores a posiciones
        value_to_position = {
            'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
        }
        
        return value_to_position.get(value, 13)