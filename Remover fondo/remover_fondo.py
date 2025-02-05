from PIL import Image
from rembg import remove
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class BackgroundRemover:
    def __init__(self, gui):
        self.gui = gui

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.gui,
            "Selecciona la imagen de origen",
            "",
            "Archivos de imagen (*.jpg *.jpeg *.png)"
        )
        if file_path:
            self.gui.entry_origen.setText(file_path)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.gui,
            "Guardar imagen sin fondo",
            "",
            "Imagen PNG (*.png)"
        )
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
            self.gui.entry_destino.setText(file_path)

    def remove_background(self):
        ruta_origen = self.gui.entry_origen.text()
        ruta_destino = self.gui.entry_destino.text()

        if not ruta_origen or not ruta_destino:
            QMessageBox.critical(self.gui, "Error", 
                               "Debes seleccionar tanto la ruta de origen como la de destino.")
            self.gui.finish_processing()
            return

        try:
            # Actualizar progreso
            self.gui.progress_bar.setValue(20)
            
            # Cargar imagen
            imagen_base = Image.open(ruta_origen)
            self.gui.progress_bar.setValue(40)
            
            # Procesar imagen
            output = self.remove_background_logic(imagen_base)
            self.gui.progress_bar.setValue(80)
            
            # Guardar resultado
            output.save(ruta_destino)
            self.gui.progress_bar.setValue(100)
            
            QMessageBox.information(self.gui, "Éxito", 
                                  "Imagen procesada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self.gui, "Error", 
                               f"Ha ocurrido un error: {str(e)}")
        finally:
            self.gui.finish_processing()

    def remove_background_logic(self, image):
        return remove(image)
