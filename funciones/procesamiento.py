"""Aplicación del fondo a los PDFs, sin dependencias de la interfaz."""
import os
import time
from pypdf import PdfReader, PdfWriter, Transformation, PageObject
from .utilidades import acortar_texto_ui

def procesar_pdfs_background(ruta_fondo, salida, rutas_a_procesar, processing_queue, cancel_requested):
    """Procesa cada PDF y publica eventos en processing_queue.

    cancel_requested es una función sin argumentos que devuelve True al
    solicitar cancelar. El consumidor de la cola interpreta los eventos
    status, substatus, progress_mode, progress, completed, error y cancelled.
    """
    inicio = time.time()
    procesados, errores = (0, [])
    total = len(rutas_a_procesar)
    try:
        processing_queue.put(('status', 'Cargando archivo de fondo...', 0))
        fondo_page = PdfReader(ruta_fondo).pages[0]
        processing_queue.put(('status', 'Iniciando procesamiento...', 0))
        processing_queue.put(('progress_mode', 'determinate', total))
        for i, archivo in enumerate(rutas_a_procesar):
            if cancel_requested():
                processing_queue.put(('cancelled', '', 0))
                return
            nombre = os.path.basename(archivo)
            nombre_ui = acortar_texto_ui(nombre)
            processing_queue.put(('status', f'Procesando: {nombre_ui}', i))
            try:
                reader = PdfReader(archivo)
                writer = PdfWriter()
                for page_num, page in enumerate(reader.pages):
                    if cancel_requested():
                        processing_queue.put(('cancelled', '', 0))
                        return
                    if len(reader.pages) > 10:
                        sub_progress = f'Procesando: {nombre_ui} (página {page_num + 1}/{len(reader.pages)})'
                        processing_queue.put(('substatus', sub_progress, i))
                    base = PageObject.create_blank_page(width=page.mediabox.width, height=page.mediabox.height)
                    scale_x = page.mediabox.width / fondo_page.mediabox.width
                    scale_y = page.mediabox.height / fondo_page.mediabox.height
                    base.merge_transformed_page(fondo_page, Transformation().scale(scale_x, scale_y))
                    base.merge_page(page)
                    writer.add_page(base)
                destino = os.path.join(salida, nombre) if salida else archivo
                with open(destino, 'wb') as f:
                    writer.write(f)
                procesados += 1
                del reader
            except Exception as e:
                errores.append(f'{nombre} → {str(e)[:100]}...')
            porcentaje = int((i + 1) / total * 100)
            status_msg = f'Completado: {nombre_ui} ({i + 1}/{total} - {porcentaje}%)'
            processing_queue.put(('progress', status_msg, i + 1))
    except Exception as e:
        processing_queue.put(('error', f'Error crítico: {str(e)}', 0))
        return
    duracion = round(time.time() - inicio, 2)
    processing_queue.put(('completed', '', duracion, procesados, errores, salida))
