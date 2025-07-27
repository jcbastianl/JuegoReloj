# Solitario Reloj (Clock Solitaire)

Un juego de solitario implementado en Python usando Tkinter con arquitectura MVC (Modelo-Vista-Controlador).

## 📖 Descripción

El Solitario Reloj es un juego de cartas donde las cartas se organizan en forma de reloj (posiciones 1-12) más una posición central (13). El objetivo es revelar todas las cartas siguiendo las reglas del juego.

## 🎮 Cómo jugar

### Reglas básicas:
1. **Inicio**: Se revela la primera carta del montón central (posición 13)
2. **Movimiento**: El valor de la carta determina a qué montón va:
   - As → montón 1
   - 2 → montón 2
   - ...
   - J (11) → montón 11
   - Q (12) → montón 12
   - K (13) → vuelve al centro
3. **Progreso**: Al mover una carta, se revela automáticamente la siguiente carta del montón destino
4. **Victoria**: Ganas si logras revelar todas las cartas
5. **Derrota**: Pierdes si aparecen 4 Reyes antes de revelar todas las cartas

### Modos de juego:
- **Modo Automático**: El juego se ejecuta automáticamente
- **Modo Manual**: Debes hacer clic en la posición correcta para cada carta

## 🚀 Instalación y Ejecución

### Requisitos:
- Python 3.7 o superior
- Tkinter (incluido con Python)
- Pillow (para manejo de imágenes)

### Instalación:
```bash
git clone https://github.com/jcbastianl/JuegoReloj.git
cd JuegoReloj
pip install Pillow
```

### Ejecución:
```bash
python app.py
```

## 📁 Estructura del Proyecto

```
SolitarioReloj/
├── app.py              # Archivo principal de la aplicación
├── gamecontroller.py   # Controlador del juego (lógica de control)
├── gamemodel.py        # Modelo del juego (lógica de negocio)
├── gameview.py         # Vista del juego (interfaz gráfica)
├── assets.py           # Gestor de recursos (imágenes)
├── cartas_img/         # Carpeta con imágenes de cartas
└── README.md           # Este archivo
```

## 🏗️ Arquitectura

El proyecto sigue el patrón de diseño **MVC (Modelo-Vista-Controlador)**:

- **Modelo (`gamemodel.py`)**: Contiene la lógica del juego, reglas, estado de las cartas
- **Vista (`gameview.py`)**: Maneja la interfaz gráfica y la visualización
- **Controlador (`gamecontroller.py`)**: Coordina la interacción entre modelo y vista

## 🎯 Características

- ✅ Interfaz gráfica intuitiva
- ✅ Modo automático y manual
- ✅ Visualización en forma de reloj
- ✅ Contador de cartas ocultas
- ✅ Resaltado de carta actual
- ✅ Mensajes informativos
- ✅ Detección automática de victoria/derrota

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado con ❤️ usando Python y Tkinter
