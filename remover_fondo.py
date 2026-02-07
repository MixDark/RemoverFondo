from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PIL import Image
from rembg import remove

class BackgroundRemover:
    def __init__(self, app):
        self.app = app

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.app,
            "Selecciona la imagen de origen",
            "",
            "Archivos de imagen (*.jpg *.jpeg *.png)"
        )
        
        if file_path:
            self.app.entry_origen.setText(file_path)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.app,
            "Guardar imagen sin fondo",
            "",
            "Imagen PNG (*.png)"
        )
        
        if file_path:
            self.app.entry_destino.setText(file_path)

    def remove_background(self):
        ruta_origen = self.app.entry_origen.text()
        ruta_destino = self.app.entry_destino.text()

        if not ruta_origen or not ruta_destino:
            QMessageBox.critical(self.app, "Error", "Debes seleccionar tanto la ruta de origen como la de destino.")
            return

        try:
            imagen_base = Image.open(ruta_origen)
            output = self.remove_background_logic(imagen_base)
            output.save(ruta_destino)
            QMessageBox.information(self.app, "Éxito", "Imagen procesada correctamente")
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Ha ocurrido un error: {e}")

    def remove_background_logic(self, image):
        return remove(image)