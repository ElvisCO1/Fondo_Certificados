"""Estado, acciones del usuario y coordinación del procesamiento."""
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from queue import Queue, Empty
from .arrastrar import crear_ventana
from .configuracion import ConfiguracionMixin
from .estilos import configurar_estilos
from .estilos import TEXT_SECONDARY, ACCENT_GREEN, ACCENT_RED
from .procesamiento import procesar_pdfs_background
from .utilidades import acortar_texto_ui, open_folder
from .vista import construir_interfaz
from .identidad import NOMBRE_APP, cargar_logos

class AplicacionPDF(ConfiguracionMixin):
    def __init__(self):
        self.root = crear_ventana()
        self.root.title(NOMBRE_APP)
        self.logos = cargar_logos(self.root)
        self.root.iconphoto(True, self.logos[32], self.logos[16])
        self.root.configure(bg="#FAFAFA")
        self.root.grid_columnconfigure(0, weight=1)
        self.style = configurar_estilos(self.root)
        self.rutas_pdfs = set()
        self.proceso_finalizado = False
        self.processing_thread = None
        self.processing_queue = Queue()
        self.cancel_processing = False
        self.tipo_fondo_var = tk.StringVar(master=self.root, value="Acreditado")
        self.entry_fondo_acreditado = tk.StringVar(master=self.root)
        self.entry_fondo_no_acreditado = tk.StringVar(master=self.root)
        self.output_folder = tk.StringVar(master=self.root)
        self.btn_combinar = None
        construir_interfaz(self)
        self.cargar_configuracion()
        self.actualizar_listbox()
        self.actualizar_boton_combinar()
        self.output_folder.trace_add("write", self.actualizar_boton_combinar)

    def ejecutar(self):
        self.root.mainloop()

    def seleccionar_carpeta_salida(self):
        carpeta = filedialog.askdirectory(title='Seleccionar Carpeta de Salida')
        if carpeta:
            self.output_folder.set(carpeta)
            self.guardar_configuracion()
            self.actualizar_boton_combinar()
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel) and widget.winfo_exists():
                    self.actualizar_label_carpeta_config(widget, carpeta)
            print(f'📁 Carpeta de salida: {os.path.basename(carpeta)}')

    def seleccionar_pdfs(self):
        if self.proceso_finalizado:
            messagebox.showinfo('Proceso finalizado', "El proceso anterior ya terminó.\n\nUsa 'Limpiar' antes de cargar nuevos PDFs.")
            return
        archivos = filedialog.askopenfilenames(title='Seleccionar PDFs a combinar', filetypes=[('Archivos PDF', '*.pdf')])
        if archivos:
            self.rutas_pdfs.update(archivos)
            self.actualizar_listbox()

    def actualizar_listbox(self):
        self.listbox_pdfs.delete(0, tk.END)
        for archivo in sorted(self.rutas_pdfs):
            self.listbox_pdfs.insert(tk.END, acortar_texto_ui(os.path.basename(archivo), 75))
        count = len(self.rutas_pdfs)
        if count == 0:
            self.label_status.config(text='Sin archivos')
            if not self.proceso_finalizado:
                self.label_progress.config(text='', foreground=TEXT_SECONDARY)
        else:
            self.label_status.config(text=f"{count} archivo{('s' if count != 1 else '')}")
            if not self.proceso_finalizado:
                self.label_progress.config(text='Listo para procesar', foreground=TEXT_SECONDARY)
        self.actualizar_boton_combinar()

    def limpiar_lista(self):
        self.rutas_pdfs.clear()
        self.proceso_finalizado = False
        self.actualizar_listbox()
        self.label_progress.config(text='Lista limpiada. Ya puedes cargar nuevos PDFs.', foreground=TEXT_SECONDARY)
        self.actualizar_boton_combinar()

    def eliminar_seleccionado(self):
        seleccion = self.listbox_pdfs.curselection()
        if not seleccion:
            messagebox.showwarning('Aviso', 'Selecciona un archivo para eliminar.')
            return
        rutas = sorted(self.rutas_pdfs)
        self.rutas_pdfs.clear()
        for i, ruta in enumerate(rutas):
            if i not in seleccion:
                self.rutas_pdfs.add(ruta)
        self.actualizar_listbox()

    def drop(self, event):
        if self.proceso_finalizado:
            messagebox.showinfo('Proceso finalizado', 'Limpia la lista actual antes de arrastrar nuevos PDFs.')
            return
        archivos = self.root.splitlist(event.data)
        for archivo in archivos:
            if archivo.lower().endswith('.pdf') and os.path.exists(archivo):
                self.rutas_pdfs.add(archivo)
        self.actualizar_listbox()

    def actualizar_boton_combinar(self, *args):
        ruta = self.output_folder.get()
        if not self.btn_combinar:
            return
        if self.proceso_finalizado:
            self.label_output_mode.config(text='', foreground='gray')
            self.btn_combinar.config(text='🚀 Combinar', state='disabled')
            return
        if self.rutas_pdfs and (ruta and os.path.isdir(ruta)):
            carpeta = acortar_texto_ui(os.path.basename(ruta) or ruta, 35)
            self.label_output_mode.config(text=f'✔ Guardando en: {carpeta}', foreground=ACCENT_GREEN)
            self.btn_combinar.config(text='🚀 Combinar', state='normal')
        elif self.rutas_pdfs:
            self.label_output_mode.config(text='⚠ Sobrescribirá originales', foreground=ACCENT_RED)
            self.btn_combinar.config(text='🚀 Combinar', state='normal')
        else:
            self.label_output_mode.config(text='', foreground='gray')
            self.btn_combinar.config(text='🚀 Combinar', state='disabled')

    def combinar(self):
        """Inicia el proceso de combinación en segundo plano"""
        if self.proceso_finalizado:
            messagebox.showinfo('Limpieza requerida', "El proceso anterior ya finalizó.\n\nPulsa 'Limpiar' antes de procesar nuevos PDFs.")
            return
        opcion_fondo = self.tipo_fondo_var.get()
        ruta_fondo = self.entry_fondo_acreditado.get() if opcion_fondo == 'Acreditado' else self.entry_fondo_no_acreditado.get()
        salida = self.output_folder.get() if os.path.isdir(self.output_folder.get()) else None
        if not ruta_fondo or not os.path.exists(ruta_fondo):
            messagebox.showerror('Error de Fondo', f"El archivo de fondo para '{opcion_fondo}' no ha sido seleccionado o no existe en la ruta:\n{ruta_fondo}")
            return
        self.cancel_processing = False
        self.configurar_interfaz_procesamiento(True)
        while not self.processing_queue.empty():
            try:
                self.processing_queue.get_nowait()
            except Empty:
                break
        self.processing_thread = threading.Thread(target=procesar_pdfs_background, args=(ruta_fondo, salida, list(self.rutas_pdfs), self.processing_queue, lambda: self.cancel_processing))
        self.processing_thread.daemon = True
        self.processing_thread.start()
        self.monitorear_progreso()

    def monitorear_progreso(self):
        """Monitorea el progreso del procesamiento desde el hilo principal"""
        try:
            while True:
                try:
                    mensaje = self.processing_queue.get_nowait()
                    tipo = mensaje[0]
                    if tipo == 'status':
                        self.label_progress.config(text=mensaje[1])
                    elif tipo == 'substatus':
                        self.label_progress.config(text=mensaje[1])
                    elif tipo == 'progress_mode':
                        self.progress_bar['mode'] = mensaje[1]
                        if mensaje[1] == 'determinate':
                            self.progress_bar['maximum'] = mensaje[2]
                    elif tipo == 'progress':
                        self.label_progress.config(text=mensaje[1])
                        self.progress_bar['value'] = mensaje[2]
                    elif tipo == 'completed':
                        duracion, procesados, errores, salida = mensaje[2:]
                        self.finalizar_procesamiento(duracion, procesados, errores, salida)
                        return
                    elif tipo == 'error':
                        self.progress_bar.grid_remove()
                        self.configurar_interfaz_procesamiento(False)
                        messagebox.showerror('Error crítico', mensaje[1])
                        return
                    elif tipo == 'cancelled':
                        self.progress_bar.grid_remove()
                        self.configurar_interfaz_procesamiento(False)
                        self.label_progress.config(text='❌ Proceso cancelado', foreground=ACCENT_RED)
                        self.root.after(3000, lambda: self.label_progress.config(text='Listo para comenzar', foreground=TEXT_SECONDARY))
                        return
                except Empty:
                    break
        except Exception as e:
            print(f'Error en monitoreo: {e}')
        if self.processing_thread and self.processing_thread.is_alive():
            self.root.after(100, self.monitorear_progreso)
        else:
            self.configurar_interfaz_procesamiento(False)

    def configurar_interfaz_procesamiento(self, iniciando):
        """Configura la interfaz para mostrar/ocultar elementos de procesamiento"""
        if iniciando:
            if self.btn_combinar:
                self.btn_combinar.config(text='❌ Cancelar', command=self.cancelar_procesamiento, state='normal')
            self.progress_bar['mode'] = 'indeterminate'
            self.progress_bar.start()
            self.progress_bar.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(4, 0))
            for widget in [self.btn_configuracion, self.combo_tipo_fondo]:
                widget.config(state='disabled')
            for child in self.actions_frame.winfo_children():
                if isinstance(child, ttk.Button) and child != self.btn_combinar:
                    child.config(state='disabled')
        else:
            if self.btn_combinar:
                self.btn_combinar.config(text='🚀 Combinar', command=self.combinar, state='normal')
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            for widget in [self.btn_configuracion, self.combo_tipo_fondo]:
                widget.config(state='normal')
            for child in self.actions_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state='normal')

    def cancelar_procesamiento(self):
        """Cancela el procesamiento en curso"""
        respuesta = messagebox.askyesno('Cancelar Proceso', '¿Estás seguro de que deseas cancelar el procesamiento?\n\nLos archivos ya procesados se mantendrán.')
        if respuesta:
            self.cancel_processing = True
            self.btn_combinar.config(text='⏳ CANCELANDO...', state='disabled')
            self.label_progress.config(text='Cancelando proceso...')

    def finalizar_procesamiento(self, duracion, procesados, errores, salida):
        """Finaliza el procesamiento y muestra resultados"""
        self.proceso_finalizado = True
        self.configurar_interfaz_procesamiento(False)
        if errores:
            mensaje_errores = '\n'.join(errores[:10])
            if len(errores) > 10:
                mensaje_errores += f'\n... y {len(errores) - 10} errores más'
            messagebox.showwarning('Completado con errores', f'Proceso finalizado en {duracion}s.\n\n✅ Procesados exitosamente: {procesados}\n❌ Errores encontrados: {len(errores)}\n\nDetalles de errores:\n{mensaje_errores}')
            self.label_progress.config(text=f'⚠️ Completado con {len(errores)} errores ({duracion}s)', foreground=ACCENT_RED)
        else:
            destino_txt = os.path.basename(salida) if salida else 'ubicaciones originales'
            destino_ui = acortar_texto_ui(destino_txt, 35)
            self.label_progress.config(text=f'✅ ¡Éxito! {procesados} PDFs combinados en {duracion}s - {destino_ui}', foreground=ACCENT_GREEN)
        self.actualizar_boton_combinar()

    def mostrar_menu_contextual(self, event):
        try:
            index = self.listbox_pdfs.nearest(event.y)
            if 0 <= index < self.listbox_pdfs.size():
                self.listbox_pdfs.selection_clear(0, tk.END)
                self.listbox_pdfs.selection_set(index)
                self.listbox_pdfs.activate(index)
                menu_contextual = tk.Menu(self.root, tearoff=0)
                menu_contextual.add_command(label='🗑 Eliminar este archivo', command=self.eliminar_seleccionado)
                menu_contextual.add_separator()
                menu_contextual.add_command(label='📋 Mostrar ruta completa', command=self.mostrar_ruta_seleccionada)
                menu_contextual.add_command(label='📁 Abrir ubicación', command=self.abrir_ubicacion_seleccionada)
                menu_contextual.tk_popup(event.x_root, event.y_root)
        except:
            pass

    def mostrar_ruta_seleccionada(self):
        seleccion = self.listbox_pdfs.curselection()
        if seleccion:
            rutas = sorted(self.rutas_pdfs)
            ruta = rutas[seleccion[0]]
            messagebox.showinfo('Ruta del archivo', ruta)

    def abrir_ubicacion_seleccionada(self):
        seleccion = self.listbox_pdfs.curselection()
        if seleccion:
            rutas = sorted(self.rutas_pdfs)
            ruta = rutas[seleccion[0]]
            carpeta = os.path.dirname(ruta)
            open_folder(carpeta)
