"""Persistencia y ventana de configuración de AplicacionPDF.

Este componente usa las variables y controles de su instancia de aplicación.
"""
import json
import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfReader
from .estilos import BG_PRIMARY, ACCENT_GREEN

CONFIG_FILE = Path(__file__).resolve().parent.parent / "pdf_combiner_config.json"

class ConfiguracionMixin:
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo JSON"""
        if not os.path.exists(CONFIG_FILE):
            self.guardar_configuracion()
            return
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'ruta_fondo_acreditado' in config and os.path.exists(config['ruta_fondo_acreditado']):
                    self.entry_fondo_acreditado.set(config['ruta_fondo_acreditado'])
                if 'ruta_fondo_no_acreditado' in config and os.path.exists(config['ruta_fondo_no_acreditado']):
                    self.entry_fondo_no_acreditado.set(config['ruta_fondo_no_acreditado'])
                if 'ruta_salida' in config and os.path.isdir(config['ruta_salida']):
                    self.output_folder.set(config['ruta_salida'])
                print(f'✅ Configuración cargada desde {CONFIG_FILE}')
        except Exception as e:
            print(f'⚠️ Error al cargar configuración: {e}')
            self.guardar_configuracion()

    def guardar_configuracion(self):
        """Guarda la configuración actual en el archivo JSON"""
        config = {'ruta_fondo_acreditado': self.entry_fondo_acreditado.get(), 'ruta_fondo_no_acreditado': self.entry_fondo_no_acreditado.get(), 'ruta_salida': self.output_folder.get(), 'version': '1.0', 'ultima_actualizacion': time.strftime('%Y-%m-%d %H:%M:%S')}
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f'💾 Configuración guardada en {CONFIG_FILE}')
        except Exception as e:
            print(f'❌ Error al guardar configuración: {e}')
            messagebox.showerror('Error de Guardado', f'No se pudo guardar la configuración:\n{str(e)}')

    def abrir_configuracion(self):
        """Abre la ventana modal de configuración"""
        config_window = tk.Toplevel(self.root)
        config_window.title('⚙️ Configuración')
        config_window.geometry('380x180')
        config_window.resizable(False, False)
        config_window.configure(bg=BG_PRIMARY)
        config_window.transient(self.root)
        config_window.grab_set()
        config_window.update_idletasks()
        x = config_window.winfo_screenwidth() // 2 - 380 // 2
        y = config_window.winfo_screenheight() // 2 - 180 // 2
        config_window.geometry(f'380x180+{x}+{y}')
        main_frame = ttk.Frame(config_window)
        main_frame.pack(fill='both', expand=True, padx=12, pady=12)
        main_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(main_frame, text='Fondo Acreditado:', style='TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=3)
        label_estado_acreditado = ttk.Label(main_frame, text='⚠ No configurado', style='Secondary.TLabel')
        label_estado_acreditado.grid(row=0, column=1, sticky='w', padx=(0, 10), pady=3)
        ttk.Button(main_frame, text='📂', width=3, command=lambda: self.seleccionar_fondo_config('acreditado')).grid(row=0, column=2, pady=3)
        ttk.Label(main_frame, text='Fondo No Acreditado:', style='TLabel').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=3)
        label_estado_no_acreditado = ttk.Label(main_frame, text='⚠ No configurado', style='Secondary.TLabel')
        label_estado_no_acreditado.grid(row=1, column=1, sticky='w', padx=(0, 10), pady=3)
        ttk.Button(main_frame, text='📂', width=3, command=lambda: self.seleccionar_fondo_config('no_acreditado')).grid(row=1, column=2, pady=3)
        ttk.Label(main_frame, text='Carpeta Salida:', style='TLabel').grid(row=2, column=0, sticky='w', padx=(0, 10), pady=3)
        label_estado_carpeta = ttk.Label(main_frame, text='(Sobrescribir originales)', style='Secondary.TLabel')
        label_estado_carpeta.grid(row=2, column=1, sticky='w', padx=(0, 10), pady=3)
        ttk.Button(main_frame, text='📂', width=3, command=self.seleccionar_carpeta_salida).grid(row=2, column=2, pady=3)
        if self.entry_fondo_acreditado.get():
            label_estado_acreditado.config(text='✓ Configurado', foreground=ACCENT_GREEN)
        if self.entry_fondo_no_acreditado.get():
            label_estado_no_acreditado.config(text='✓ Configurado', foreground=ACCENT_GREEN)
        if self.output_folder.get():
            nombre_carpeta = os.path.basename(self.output_folder.get()) or 'Raíz'
            label_estado_carpeta.config(text=f'📁 {nombre_carpeta}', foreground=ACCENT_GREEN)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(12, 0))
        ttk.Button(buttons_frame, text='❌ Cancelar', style='Minimal.TButton', command=config_window.destroy).pack(side='right', padx=(5, 0))
        ttk.Button(buttons_frame, text='✅ Guardar', style='Primary.TButton', command=lambda: self.guardar_y_cerrar(config_window)).pack(side='right', padx=(0, 5))

    def seleccionar_fondo_config(self, tipo):
        """Selecciona archivo de fondo desde la ventana de configuración"""
        archivo = filedialog.askopenfilename(title=f"Seleccionar Fondo {('Acreditado' if tipo == 'acreditado' else 'No Acreditado')}", filetypes=[('Archivos PDF', '*.pdf')])
        if archivo:
            try:
                PdfReader(archivo)
                if tipo == 'acreditado':
                    self.entry_fondo_acreditado.set(archivo)
                    for widget in self.root.winfo_children():
                        if isinstance(widget, tk.Toplevel) and widget.winfo_exists():
                            self.actualizar_labels_config(widget, 'acreditado')
                else:
                    self.entry_fondo_no_acreditado.set(archivo)
                    for widget in self.root.winfo_children():
                        if isinstance(widget, tk.Toplevel) and widget.winfo_exists():
                            self.actualizar_labels_config(widget, 'no_acreditado')
                self.guardar_configuracion()
                print(f"✅ Archivo de fondo {('acreditado' if tipo == 'acreditado' else 'no acreditado')} configurado")
            except Exception:
                messagebox.showerror('Error', 'Archivo PDF inválido o dañado.')

    def actualizar_labels_config(self, ventana, tipo):
        """Actualiza los labels de estado en la ventana de configuración"""

        def buscar_y_actualizar(widget):
            for child in widget.winfo_children():
                if hasattr(child, 'winfo_children'):
                    buscar_y_actualizar(child)
                if isinstance(child, ttk.Label):
                    grid_info = child.grid_info()
                    if grid_info:
                        row = grid_info.get('row')
                        column = grid_info.get('column')
                        if tipo == 'acreditado' and row == 0 and (column == 1):
                            child.config(text='✓ Configurado', foreground=ACCENT_GREEN)
                        elif tipo == 'no_acreditado' and row == 1 and (column == 1):
                            child.config(text='✓ Configurado', foreground=ACCENT_GREEN)
        buscar_y_actualizar(ventana)

    def actualizar_label_carpeta_config(self, ventana, carpeta):
        """Actualiza el label de carpeta de salida en la ventana de configuración"""
        nombre_carpeta = os.path.basename(carpeta) or 'Raíz'

        def buscar_y_actualizar_carpeta(widget):
            for child in widget.winfo_children():
                if hasattr(child, 'winfo_children'):
                    buscar_y_actualizar_carpeta(child)
                if isinstance(child, ttk.Label):
                    grid_info = child.grid_info()
                    if grid_info and grid_info.get('row') == 2 and (grid_info.get('column') == 1):
                        child.config(text=f'📁 {nombre_carpeta}', foreground=ACCENT_GREEN)
        buscar_y_actualizar_carpeta(ventana)

    def guardar_y_cerrar(self, window):
        """Guarda la configuración y cierra la ventana"""
        self.guardar_configuracion()
        self.actualizar_boton_combinar()
        window.destroy()
