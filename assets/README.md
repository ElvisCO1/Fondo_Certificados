# Logo de la aplicación

`logo.png` es la versión PNG transparente del símbolo proporcionado por Elvis Candia Ochoa, preparada con la herramienta integrada `imagegen`. No incluye el texto «Qhapaq». Se utiliza en el icono de ventana y «Acerca de».

Tkinter carga el archivo desde una ruta relativa al código y lo reduce para cada ubicación; no requiere Pillow. Mantén la carpeta `assets` junto a `main.py` al distribuir el proyecto.

## Instrucción utilizada para preparar el recurso

```text
Edit the last attached logo (symbol only) for use as a small desktop application icon. Use case: background-extraction / precise-object-edit. Preserve the exact central blue/cyan Q-shaped ring with mountain and winding turquoise river, its proportions and original flat gradient style. Remove the dark rectangular background completely including the dark negative spaces inside the ring: actual transparent alpha background. Remove any detached blue cropped fragment or stray border outside the main symbol, keep the intentional river tail of the Q. No text, no word Qhapaq, no extra shapes, no drop shadow, no border. Center the complete symbol on a square transparent canvas with small even padding, not clipped. Output a transparent PNG.
```
