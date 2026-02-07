# 🎨 Eliminador de fondo con IA

Una aplicación de escritorio moderna y potente construida con Python y PyQt6 que permite eliminar el fondo de imágenes de forma automática utilizando Inteligencia Artificial avanzada.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![Rembg](https://img.shields.io/badge/AI-Rembg-orange.svg)

## ✨ Características

- **Eliminación de fondo automática**: Utiliza la librería `rembg` (basada en U2Net) para resultados de alta precisión.
- **Interfaz moderna**: Diseño limpio y amigable inspirado en principios de diseño moderno.
- **Soporte drag & drop**: (Próximamente/En desarrollo) Interfaz intuitiva.
- **Vista previa**: Visualiza la imagen original antes de procesarla.
- **Opciones de calidad**: Ajusta la calidad de compresión del archivo de salida.
- **Múltiples formatos**: Soporte para guardar en PNG (transparente), JPG (fondo negro/blanco), etc.
- **Respaldo automático**: Opción para crear copias de seguridad de archivos sobrescritos.
- **Procesamiento asíncrono**: La interfaz no se congela durante el procesamiento de imágenes pesadas.

## 🚀 Instalación

1.  **Clonar el repositorio** (o descargar el código):
    ```bash
    git clone <tu-repositorio>
    cd "Remover fondo"
    ```

2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

    *Nota: Si tienes tarjeta gráfica NVIDIA, puedes editar `requirements.txt` para usar `rembg[gpu]` para mayor velocidad.*

## 🛠️ Uso

1.  Ejecuta la aplicación:
    ```bash
    python interfaz_grafica.py
    ```
2.  Haz clic en **"📂 Seleccionar"** para abrir una imagen.
3.  La aplicación sugerirá automáticamente un nombre de salida (ej: `imagen_sf.png`).
4.  Ajusta la calidad si es necesario.
5.  Haz clic en **"✨ Eliminar fondo"**.
6.  ¡Listo! La imagen procesada se guardará en la ruta indicada.

## 📋 Requisitos

- Python 3.10 o superior.
- Dependencias (ver `requirements.txt`):
    - `PyQt6`
    - `rembg`
    - `Pillow`
    - `opencv-python`
    - `numpy`
    - `onnxruntime` (instalado automáticamente con rembg)

## 🐛 Solución de problemas comunes

**Error: "No onnxruntime backend found"**
Si persiste, intenta reinstalar:
```bash
pip install --force-reinstall "rembg[cpu]"
```

## 📝 Licencia

Este proyecto es de uso libre para fines educativos y personales.
