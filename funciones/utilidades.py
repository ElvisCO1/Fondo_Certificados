"""Formato de textos y apertura de carpetas."""
import os
import subprocess

MAX_TEXTO_UI = 60

def acortar_texto_ui(texto, max_len=MAX_TEXTO_UI):
    """Recorta textos largos para evitar que la ventana crezca."""
    texto = str(texto)
    if len(texto) <= max_len:
        return texto
    return texto[:max_len - 3] + '...'

def open_folder(path):
    """Abre la carpeta en el explorador de archivos del sistema operativo."""
    from tkinter import messagebox
    try:
        if os.name == 'nt':
            os.startfile(path)
        elif os.sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    except FileNotFoundError:
        messagebox.showerror('Error de Apertura', f'Comando del sistema operativo no encontrado para abrir la carpeta.')
    except Exception as e:
        messagebox.showerror('Error de Apertura', f'No se pudo abrir la carpeta. Asegúrate de que la ruta exista:\n{path}\nDetalle: {e}')
