# assets.py
import os
from PIL import Image, ImageTk

class AssetManager:
    def __init__(self):
        self.images = {}
        self._load_images()
    
    def _load_images(self):
        """Carga todas las imágenes de cartas."""
        img_path = "cartas_img"
        if not os.path.exists(img_path):
            print(f"Error: La carpeta '{img_path}' no fue encontrada.")
            return

        # Mapeo de nombres de archivo a nombres de juego
        suits_map = {'club': '♣', 'diamond': '♦', 'heart': '♥', 'spade': '♠'}
        values_map_to_file = {'A': '1', 'J': 'jack', 'Q': 'queen', 'K': 'king'}

        try:
            # Cargar imagen de reverso
            img_file = os.path.join(img_path, "back.png")
            back_img = Image.open(img_file).resize((75, 110))
            self.images['back'] = ImageTk.PhotoImage(back_img)

            # Cargar todas las cartas
            for palo_symbol in suits_map.values():
                for valor in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
                    card_name = f"{valor}{palo_symbol}"
                    
                    # Construir el nombre del archivo
                    palo_file = [k for k, v in suits_map.items() if v == palo_symbol][0]
                    valor_file = values_map_to_file.get(valor, valor)
                    
                    filename = f"{palo_file}_{valor_file}.png"
                    filepath = os.path.join(img_path, filename)
                    
                    if os.path.exists(filepath):
                        img = Image.open(filepath).resize((75, 110))
                        self.images[card_name] = ImageTk.PhotoImage(img)
                    else:
                        print(f"Advertencia: No se encontró la imagen {filepath}")

        except Exception as e:
            print(f"Error cargando las imágenes: {e}")
            # Aquí se podría crear una imagen placeholder si fallara la carga
            pass

    def get_image(self, card_name):
        return self.images.get(card_name, self.images.get('back'))