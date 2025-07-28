# app.py - Archivo Principal del Juego Solitario Reloj
# Este es el punto de entrada del programa que inicia la aplicación

import tkinter as tk
from gamecontroller import ControladorJuego

class Aplicacion(tk.Tk):
    """
    Clase principal de la aplicación que crea la ventana principal del juego.
    
    Esta clase:
    - Configura la ventana principal con título y dimensiones
    - Inicializa el controlador del juego que maneja toda la lógica
    - Establece las propiedades básicas de la interfaz
    """
    
    def __init__(self):
        """
        Inicializa la aplicación principal del Solitario Reloj.
        
        Configura:
        - Título de la ventana
        - Tamaño fijo de la ventana (800x700 pixels)
        - Deshabilita el redimensionamiento para mantener el diseño
        - Crea el controlador principal del juego
        """
        super().__init__()
        self.title("Solitario Reloj MVC")  # Título que aparece en la barra de título
        self.geometry("800x700")  # Dimensiones de la ventana en pixels
        self.resizable(False, False)  # Impide que el usuario redimensione la ventana
        
        # Crear el controlador principal que maneja toda la lógica del juego
        controlador = ControladorJuego(self)

if __name__ == "__main__":
    # Punto de entrada del programa
    # Solo se ejecuta si este archivo se ejecuta directamente (no si se importa)
    aplicacion = Aplicacion()
    aplicacion.mainloop()  # Inicia el bucle principal de la interfaz gráfica