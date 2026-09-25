# Fondo_Certificados

Aplicación de escritorio en Python para aplicar fondos a certificados PDF generados desde hojas de cálculo, sin incluir el fondo en la propia hoja. Permite procesar varios archivos y elegir entre fondos para certificados acreditados y no acreditados.

## Requisitos

- Python 3.12 (versión utilizada para verificar las pruebas).
- Tkinter, incluido en la instalación estándar de Python para Windows.
- Dependencias indicadas en `requirements.txt`.
- `tkinterdnd2` es opcional y permite arrastrar PDFs a la ventana.

## Instalación en Windows

Desde PowerShell:

```powershell
git clone https://github.com/ElvisCO1/Fondo_Certificados.git
cd Fondo_Certificados
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para habilitar también el arrastre de archivos:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-optional.txt
```

## Ejecución y uso

```powershell
.\.venv\Scripts\python.exe main.py
```

1. Abre la configuración y selecciona los fondos PDF y una carpeta de salida existente.
2. Selecciona el tipo de fondo: acreditado o no acreditado.
3. Añade los certificados con el botón **Añadir** o arrástralos a la lista si instalaste el soporte opcional.
4. Pulsa **Combinar** y espera el resultado.
5. Usa **Limpiar** antes de iniciar un nuevo lote.

La aplicación utiliza la primera página del PDF de fondo y la ajusta al ancho y alto de cada página del certificado. Las rutas elegidas se guardan automáticamente en `pdf_combiner_config.json`, junto a `main.py`.

> **Guardado:** si no hay una carpeta de salida válida, la aplicación sobrescribe los originales. Usa copias de respaldo y una carpeta de salida diferente. Archivos con el mismo nombre comparten destino y pueden reemplazarse. Evita cerrar la aplicación mientras está escribiendo PDFs. Cancelar el procesamiento conserva los archivos ya procesados.

## Estructura

```text
main.py                      Entrada de la aplicación
funciones/
  aplicacion.py              Estado, acciones e hilo de procesamiento
  vista.py                   Controles de la interfaz
  procesamiento.py           Composición y guardado de PDFs
  configuracion.py           Configuración y persistencia JSON
  estilos.py                 Colores y estilos
  arrastrar.py               Soporte opcional de arrastre
  utilidades.py              Textos y apertura de carpetas
tests/test_procesamiento.py   Pruebas automatizadas
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas generan PDFs temporales y verifican la composición, las dimensiones, la conservación del original al usar otra carpeta, la cancelación inicial, el manejo de archivos inválidos y la importación sin abrir ventanas.

GitHub Actions ejecuta estas pruebas en Windows con Python 3.12 en cada `push` y `pull_request`, y permite iniciarlas manualmente.

## Archivos locales

El `.gitignore` excluye entornos virtuales, cachés de Python, configuración con rutas locales, archivos `.env` y PDFs. Los certificados y fondos se seleccionan desde el equipo y no se incluyen en el repositorio. Las pruebas no necesitan PDFs versionados.
