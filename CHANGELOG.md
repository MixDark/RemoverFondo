# Changelog

Todas las mejoras notables en el proyecto "Eliminador de Fondo" serán documentadas en este archivo.

## [1.1.0] - 2026-02-07

### ✨ Añadido
- **Manejo de errores robusto**: Detección automática de problemas con el backend de `onnxruntime` y sugerencias de solución en la interfaz.
- **Script de instalación**: Nuevo archivo `setup.bat` para facilitar la instalación de dependencias en Windows.
- **Documentación**: Añadidos `README.md` y `CHANGELOG.md` para mejor gestión del proyecto.
- **Icono**: Añadido `favicon.ico` a la aplicación.
- **Dependencias**: Archivo `requirements.txt` actualizado y verificado.

### 🔧 Corregido
- **Conflicto de DLLs**: Solucionado el error crítico "No onnxruntime backend found" reorganizando los imports para cargar `onnxruntime` antes que `PyQt6`.
- **Compatibilidad**: Forzada la instalación de `rembg[cpu]` para garantizar funcionamiento en equipos sin GPU dedicada configurada.

## [1.0.0] - 2026-02-03

### ✨ Añadido
- **Interfaz gráfica**: Primera versión con PyQt6.
- **Funcionalidad principal**: Integración de `rembg` para eliminar fondos.
- **Vista previa**: Visualización básica de la imagen seleccionada.
- **Opciones de guardado**: Selección de ruta de salida y formato.
