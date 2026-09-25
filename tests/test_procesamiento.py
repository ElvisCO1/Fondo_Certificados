"""Comprobaciones del procesamiento sin abrir la interfaz ni usar PDFs reales."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from queue import Queue

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

from funciones.procesamiento import procesar_pdfs_background


class ProcesamientoTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.output = self.base / 'salida'
        self.output.mkdir()
        self.background = self.base / 'fondo.pdf'
        self.input = self.base / 'certificado.pdf'
        self.crear_pdf(self.background, [(100, 100)], b'0 0 1 rg 0 0 100 100 re f')
        self.crear_pdf(self.input, [(200, 300), (300, 200)], b'1 0 0 rg 5 5 10 10 re f')

    @staticmethod
    def crear_pdf(path, sizes, drawing):
        writer = PdfWriter()
        for width, height in sizes:
            page = writer.add_blank_page(width=width, height=height)
            stream = DecodedStreamObject()
            stream.set_data(drawing)
            page[NameObject('/Contents')] = stream
        with path.open('wb') as file:
            writer.write(file)

    def procesar(self, paths, cancelled=lambda: False):
        queue = Queue()
        procesar_pdfs_background(
            str(self.background), str(self.output), [str(p) for p in paths],
            queue, cancelled,
        )
        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())
        return messages

    def test_combina_paginas_conservando_original_y_dimensiones(self):
        original = self.input.read_bytes()
        messages = self.procesar([self.input])
        self.assertEqual(messages[-1][0], 'completed')
        self.assertEqual(messages[-1][3:5], (1, []))
        self.assertEqual(self.input.read_bytes(), original)
        result = PdfReader(self.output / self.input.name)
        self.assertEqual(len(result.pages), 2)
        for page, size in zip(result.pages, [(200, 300), (300, 200)]):
            self.assertEqual((page.mediabox.width, page.mediabox.height), size)
            contents = page.get_contents().get_data()
            # El dibujo azul del fondo precede al dibujo rojo del certificado.
            self.assertLess(contents.index(b'0 0 1 rg'), contents.index(b'1 0 0 rg'))

    def test_cancelacion_no_crea_resultado(self):
        messages = self.procesar([self.input], lambda: True)
        self.assertEqual(messages[-1][0], 'cancelled')
        self.assertEqual(list(self.output.iterdir()), [])

    def test_pdf_invalido_no_impide_procesar_el_siguiente(self):
        invalid = self.base / 'invalido.pdf'
        invalid.write_bytes(b'no es un PDF')
        messages = self.procesar([invalid, self.input])
        self.assertEqual(messages[-1][0], 'completed')
        self.assertEqual(messages[-1][3], 1)
        self.assertEqual(len(messages[-1][4]), 1)
        self.assertTrue((self.output / self.input.name).exists())

    def test_importar_main_no_crea_ventanas(self):
        result = subprocess.run(
            [sys.executable, '-c', 'import tkinter as tk; import main; assert tk._default_root is None'],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
