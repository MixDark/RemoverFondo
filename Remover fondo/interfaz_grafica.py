import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                            QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                            QProgressBar, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from remover_fondo import BackgroundRemover

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eliminador de fondo de imágenes")
        self.setFixedSize(620, 200)
        self.setWindowIcon(QIcon('icono.png'))    
        
        # Centrar la ventana
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2),
                 int((screen.height() - self.height()) / 2))

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Lógica de procesamiento
        self.logic = BackgroundRemover(self)

        # Sección de imagen origen
        origen_layout = QHBoxLayout()
        self.label_origen = QLabel("Ruta de origen: ")
        self.entry_origen = QLineEdit()
        self.entry_origen.setFixedWidth(400)
        self.entry_origen.setReadOnly(True)
        self.button_origen = QPushButton("Seleccionar")
        self.button_origen.setFixedWidth(100)
        self.button_origen.clicked.connect(self.logic.select_image)
        
        origen_layout.addWidget(self.label_origen)
        origen_layout.addWidget(self.entry_origen)
        origen_layout.addWidget(self.button_origen)
        origen_layout.addStretch()

        # Sección de imagen destino
        destino_layout = QHBoxLayout()
        self.label_destino = QLabel("Ruta de destino:")
        self.entry_destino = QLineEdit()
        self.entry_destino.setFixedWidth(400)
        self.entry_destino.setReadOnly(True)
        self.button_destino = QPushButton("Guardar")
        self.button_destino.setFixedWidth(100)
        self.button_destino.clicked.connect(self.logic.save_image)
        
        destino_layout.addWidget(self.label_destino)
        destino_layout.addWidget(self.entry_destino)
        destino_layout.addWidget(self.button_destino)
        destino_layout.addStretch()

        # Contenedor para la barra de progreso
        self.progress_container = QWidget()
        progress_layout = QHBoxLayout(self.progress_container)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(500)
        progress_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.progress_container.hide()  # Ocultar el contenedor completo

        # Botón procesar
        button_layout = QHBoxLayout()
        self.button_procesar = QPushButton("Eliminar fondo")
        self.button_procesar.setFixedWidth(200)
        self.button_procesar.clicked.connect(self.validate_and_process)
        button_layout.addWidget(self.button_procesar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Agregar widgets al layout principal
        layout.addLayout(origen_layout)
        layout.addLayout(destino_layout)
        layout.addWidget(self.progress_container)
        layout.addLayout(button_layout)

        # Aplicar estilos CSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f8f8f8;
                color: #000000;
            }
            QLineEdit:disabled {
                background-color: #f8f8f8;
                color: #000000;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background-color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #000000;
            }
        """)

    def validate_and_process(self):
        #Validar las rutas antes de iniciar el procesamiento
        if not self.entry_origen.text() or not self.entry_destino.text():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Error")
            msg.setText("Debes seleccionar tanto la ruta de origen como la de destino.")
            msg.exec()
            return
        
        # Si la validación es exitosa, mostrar la barra y ajustar el tamaño
        self.setFixedSize(620, 250)
        self.progress_container.show()
        self.start_processing()

    def start_processing(self):
        #Iniciar el procesamiento
        self.progress_bar.setValue(0)
        self.button_procesar.setEnabled(False)
        self.logic.remove_background()

    def finish_processing(self):
        #Finalizar el procesamiento
        self.progress_bar.setValue(100)
        self.button_procesar.setEnabled(True)
        QTimer.singleShot(1000, self.hide_progress)

    def hide_progress(self):
        #Ocultar la barra de progreso y ajustar el tamaño de la ventana
        self.progress_container.hide()
        self.setFixedSize(620, 200)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
