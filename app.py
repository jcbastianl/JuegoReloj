# app.py - Archivo Principal del Juego Solitario Reloj

import tkinter as tk
from gamecontroller import ControladorJuego

class Aplicacion(tk.Tk):
    # Clase principal de la aplicación
    
    def __init__(self):
        # Configurar ventana principal
        super().__init__()
        self.title("Solitario Reloj MVC")
        self.geometry("800x700")
        self.resizable(False, False)
        
        # Crear controlador principal
        controlador = ControladorJuego(self)

if __name__ == "__main__":
    # Punto de entrada del programa
    aplicacion = Aplicacion()
    aplicacion.mainloop()