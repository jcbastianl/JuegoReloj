# assets.py - Gestor de Recursos del Juego
# Este archivo maneja la carga y gestión de todas las imágenes de cartas

import os
from PIL import Image, ImageTk

class GestorRecursos:
    """
    Clase que maneja la carga y administración de todas las imágenes del juego.
    
    Esta clase se encarga de:
    - Cargar todas las imágenes de cartas desde el directorio de recursos
    - Redimensionar las imágenes al tamaño apropiado para el juego
    - Proporcionar acceso fácil a las imágenes mediante nombres de cartas
    - Manejar errores de carga de imágenes graciosamente
    """
    
    def __init__(self):
        """
        Inicializa el gestor de recursos y carga todas las imágenes.
        """
        self.imagenes = {}  # Diccionario para almacenar todas las imágenes cargadas
        self._cargar_imagenes()
    
    def _cargar_imagenes(self):
        """
        Carga todas las imágenes de cartas desde el directorio de recursos.
        
        Este método:
        1. Verifica que existe el directorio de imágenes
        2. Carga la imagen del reverso de las cartas
        3. Carga todas las 52 cartas del juego
        4. Redimensiona todas las imágenes al tamaño estándar (75x110 pixels)
        5. Maneja errores de carga graciosamente
        """
        ruta_imagenes = "cartas_img"
        if not os.path.exists(ruta_imagenes):
            print(f"Error: La carpeta '{ruta_imagenes}' no fue encontrada.")
            return

        # Mapeo de nombres de archivo a símbolos de palos del juego
        mapa_palos = {'club': '♣', 'diamond': '♦', 'heart': '♥', 'spade': '♠'}
        
        # Mapeo de valores del juego a nombres de archivo
        mapa_valores_archivo = {'A': '1', 'J': 'jack', 'Q': 'queen', 'K': 'king'}

        try:
            # Cargar imagen del reverso de las cartas
            archivo_reverso = os.path.join(ruta_imagenes, "back.png")
            imagen_reverso = Image.open(archivo_reverso).resize((75, 110))
            self.imagenes['back'] = ImageTk.PhotoImage(imagen_reverso)

            # Cargar todas las 52 cartas del juego
            for simbolo_palo in mapa_palos.values():
                for valor in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
                    nombre_carta = f"{valor}{simbolo_palo}"
                    
                    # Construir el nombre del archivo correspondiente
                    palo_archivo = [k for k, v in mapa_palos.items() if v == simbolo_palo][0]
                    valor_archivo = mapa_valores_archivo.get(valor, valor)
                    
                    nombre_archivo = f"{palo_archivo}_{valor_archivo}.png"
                    ruta_archivo = os.path.join(ruta_imagenes, nombre_archivo)
                    
                    # Intentar cargar la imagen si existe
                    if os.path.exists(ruta_archivo):
                        imagen = Image.open(ruta_archivo).resize((75, 110))
                        self.imagenes[nombre_carta] = ImageTk.PhotoImage(imagen)
                    else:
                        print(f"Advertencia: No se encontró la imagen {ruta_archivo}")

        except Exception as e:
            print(f"Error cargando las imágenes: {e}")
            # En caso de error, el juego puede continuar sin imágenes
            # Se podría crear una imagen placeholder aquí si fuera necesario
            pass

    def obtener_imagen(self, nombre_carta):
        """
        Obtiene la imagen correspondiente a una carta específica.
        
        Args:
            nombre_carta: String que representa la carta (ej: "A♠", "K♥", "back")
            
        Returns:
            ImageTk.PhotoImage: La imagen de la carta solicitada, o la imagen del
                               reverso si la carta solicitada no se encuentra
        """
        return self.imagenes.get(nombre_carta, self.imagenes.get('back'))