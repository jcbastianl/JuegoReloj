import tkinter as tk
import os

class AssetManager:
    def __init__(self):
        self.images = {}
        self.load_images()
    
    def load_images(self):
        """Carga todas las imágenes de cartas o crea representaciones básicas"""
        try:
            from PIL import Image, ImageTk
            self._load_pil_images()
        except ImportError:
            self._create_basic_images()
    
    def _load_pil_images(self):
        """Carga imágenes usando PIL"""
        from PIL import Image, ImageTk
        
        # Ruta base de las imágenes
        img_path = "cartas_img"
        
        if not os.path.exists(img_path):
            self._create_basic_images()
            return
            
        try:
            # Cargar imagen de reverso
            back_img = Image.open(os.path.join(img_path, "back.png"))
            back_img = back_img.resize((75, 110))
            self.images['back'] = ImageTk.PhotoImage(back_img)
            
            # Cargar imágenes de cartas
            suits_map = {'club': '♣', 'diamond': '♦', 'heart': '♥', 'spade': '♠'}
            values_map = {'1': 'A', 'jack': 'J', 'queen': 'Q', 'king': 'K'}
            
            for filename in os.listdir(img_path):
                if filename.endswith('.png') and filename != 'back.png':
                    try:
                        parts = filename.replace('.png', '').split('_')
                        if len(parts) == 2:
                            suit, value = parts
                            if suit in suits_map:
                                card_value = values_map.get(value, value)
                                card_name = f"{card_value}{suits_map[suit]}"
                                
                                img = Image.open(os.path.join(img_path, filename))
                                img = img.resize((75, 110))
                                self.images[card_name] = ImageTk.PhotoImage(img)
                    except:
                        continue
        except:
            self._create_basic_images()
    
    def _create_basic_images(self):
        """Crea representaciones básicas sin PIL"""
        # No necesitamos crear imágenes reales, la vista se encarga de dibujar
        pass
    
    def get_image(self, card_name):
        """Obtiene la imagen de una carta"""
        return self.images.get(card_name, None)
