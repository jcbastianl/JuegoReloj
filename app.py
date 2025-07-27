# main.py
import tkinter as tk
from gamecontroller import GameController

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Solitario Cuadrado MVC")
        self.geometry("800x700")
        self.resizable(False, False)
        
        controller = GameController(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()