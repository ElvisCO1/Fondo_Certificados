"""Identidad visual e información de la aplicación."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from .estilos import BG_PRIMARY

NOMBRE_APP = 'Fondo de Certificados'
VERSION = '1.0.0'
AUTOR = 'Elvis Candia Ochoa'
LOGO_PATH = Path(__file__).resolve().parent.parent / 'assets' / 'logo.png'


def cargar_logos(root):
    """Carga el PNG transparente y conserva las imágenes para uso de Tkinter."""
    original = tk.PhotoImage(master=root, file=str(LOGO_PATH))
    # Tkinter permite reducir el PNG sin añadir dependencias de imágenes.
    def reducir(lado):
        factor = max(1, round(max(original.width(), original.height()) / lado))
        return original.subsample(factor, factor)

    return {lado: reducir(lado) for lado in (16, 32, 128)}


def abrir_acerca_de(app):
    """Muestra los créditos sin modificar la configuración del usuario."""
    window = tk.Toplevel(app.root)
    window.withdraw()
    window.title('Acerca de')
    window.configure(bg=BG_PRIMARY)
    window.resizable(False, False)
    window.transient(app.root)

    content = ttk.Frame(window, padding=24)
    content.pack(fill='both', expand=True)
    ttk.Label(content, image=app.logos[128]).pack(pady=(0, 12))
    ttk.Label(content, text=NOMBRE_APP, style='BrandTitle.TLabel').pack()
    ttk.Label(content, text=f'Versión {VERSION}', style='Secondary.TLabel').pack(pady=(4, 14))
    ttk.Label(content, text='Fondos para certificados PDF acreditados\ny no acreditados.',
              justify='center').pack()
    ttk.Label(content, text=f'Creado por {AUTOR}', style='Author.TLabel').pack(pady=(18, 20))
    close_button = ttk.Button(content, text='Cerrar', command=window.destroy)
    close_button.pack()
    window.bind('<Escape>', lambda event: window.destroy())
    window.update_idletasks()
    width = max(360, window.winfo_reqwidth())
    height = window.winfo_reqheight()
    x = max(0, app.root.winfo_rootx() + (app.root.winfo_width() - width) // 2)
    y = max(0, app.root.winfo_rooty() + (app.root.winfo_height() - height) // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    window.deiconify()
    window.grab_set()
    close_button.focus_set()
