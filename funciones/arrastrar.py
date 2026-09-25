"""Soporte opcional para arrastrar archivos sobre la ventana."""
import tkinter as tk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    USE_DND = True
except ImportError:
    DND_FILES = None
    TkinterDnD = None
    USE_DND = False

def crear_ventana():
    return TkinterDnD.Tk() if USE_DND else tk.Tk()
