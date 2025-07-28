# assets.py - Gestor de Recursos del Juego

import os
from PIL import Image, ImageTk

class GestorRecursos:
    # Clase para manejar las imágenes de cartas
    
    def __init__(self):
        # Inicializar y cargar todas las imágenes
        self.imagenes = {}
        self._cargar_imagenes()
    
    def _cargar_imagenes(self):
        # Cargar todas las imágenes de cartas
        ruta_imagenes = "cartas_img"
        if not os.path.exists(ruta_imagenes):
            print(f"Error: La carpeta '{ruta_imagenes}' no fue encontrada.")
            return

        # Mapeo de nombres
        mapa_palos = {'club': '♣', 'diamond': '♦', 'heart': '♥', 'spade': '♠'}
        mapa_valores_archivo = {'A': '1', 'J': 'jack', 'Q': 'queen', 'K': 'king'}

        try:
            # Cargar imagen del reverso
            archivo_reverso = os.path.join(ruta_imagenes, "back.png")
            imagen_reverso = Image.open(archivo_reverso).resize((75, 110))
            self.imagenes['back'] = ImageTk.PhotoImage(imagen_reverso)

            # Cargar todas las cartas
            for simbolo_palo in mapa_palos.values():
                for valor in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
                    nombre_carta = f"{valor}{simbolo_palo}"
                    
                    # Construir nombre del archivo
                    palo_archivo = [k for k, v in mapa_palos.items() if v == simbolo_palo][0]
                    valor_archivo = mapa_valores_archivo.get(valor, valor)
                    
                    nombre_archivo = f"{palo_archivo}_{valor_archivo}.png"
                    ruta_archivo = os.path.join(ruta_imagenes, nombre_archivo)
                    
                    # Cargar imagen si existe
                    if os.path.exists(ruta_archivo):
                        imagen = Image.open(ruta_archivo).resize((75, 110))
                        self.imagenes[nombre_carta] = ImageTk.PhotoImage(imagen)
                    else:
                        print(f"Advertencia: No se encontró la imagen {ruta_archivo}")

        except Exception as e:
            print(f"Error cargando las imágenes: {e}")
            pass

    def obtener_imagen(self, nombre_carta):
        # Obtener imagen de una carta específica
        return self.imagenes.get(nombre_carta, self.imagenes.get('back'))