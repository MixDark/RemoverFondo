import sys
import os
import onnxruntime
from rembg import remove
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFileDialog, QGroupBox, QProgressBar, QComboBox,
                             QSlider, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QImage, QIcon
from PIL import Image
import cv2
import numpy as np
try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False

class RemoveBackgroundWorker(QThread):
    """Worker thread para procesar imágenes sin bloquear la interfaz"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    progress_value = pyqtSignal(int)

    def __init__(self, input_path, output_path, quality=95):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.quality = quality

    def run(self):
        try:
            self.progress.emit("Cargando imagen")
            image = Image.open(self.input_path)
            
            self.progress.emit("Procesando imagen (esto puede tardar)")
            # Señal especial para barra indeterminada
            self.progress_value.emit(-1)
            
            # Intentar usar rembg como primera opción (mejor calidad general)
            output = None
            try:
                # from rembg import remove  <-- Eliminado, ya es global
                self.progress.emit("Usando AI Avanzada (rembg)")
                # Convertir a RGB si tiene alpha para evitar errores en rembg
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                output = remove(image)
            except Exception as e:
                print(f"Error rembg: {e}")
                
                # Intentar usar MediaPipe como segunda opción (excelente para personas/selfies)
                try:
                    self.progress.emit("Usando AI de Google (MediaPipe)")
                    output = self.remove_background_mediapipe(image)
                except Exception as e2:
                    print(f"Error mediapipe: {e2}")
                    # Fallback a OpenCV
                    self.progress.emit(f"Usando método clásico (OpenCV)")
                    output = self.remove_background_opencv(image)
            
            self.progress.emit("Guardando imagen")
            self.progress_value.emit(-1)
            output.save(self.output_path, quality=self.quality)
            
            self.progress.emit("¡Completado!")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def remove_background_mediapipe(self, image):
        """Método alternativo de alta calidad para personas usando MediaPipe"""
        if not HAS_MEDIAPIPE:
            raise ImportError("MediaPipe no está instalado")
            
        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        
        # Convertir PIL a Numpy y asegurar RGB
        image_np = np.array(image.convert('RGB'))
        
        # Crear instancia de segmentación (model_selection=1 para paisaje/cuerpo completo, 0 para general)
        with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
            # Procesar imagen
            results = selfie_segmentation.process(image_np)
            
            # Obtener máscara de segmentación
            mask = results.segmentation_mask
            
            # Aplicar umbral suave para mejorar bordes (matting)
            # La máscara viene en rango [0, 1] float
            mask = np.stack((mask,) * 3, axis=-1)
            
            # Crear imagen RGBA de salida
            image_rgba = cv2.cvtColor(image_np, cv2.COLOR_RGB2RGBA)
            
            # Asignar canal alfa basado en la máscara
            # Usar la máscara original (float) * 255 para mantener suavidad en bordes
            alpha = (results.segmentation_mask * 255).astype(np.uint8)
            image_rgba[:, :, 3] = alpha
            
            return Image.fromarray(image_rgba)

    def remove_background_opencv(self, image):
        """Método alternativo utilizando OpenCV y GrabCut mejorado"""
        try:
            # Convertir PIL Image a formato OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Añadir padding (borde) a la imagen para evitar 'recortes' en los bordes
            # esto permite que GrabCut no asuma automáticamente que los bordes de la imagen son fondo
            pad = 20
            cv_image_padded = cv2.copyMakeBorder(cv_image, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
            
            # Crear máscaras para GrabCut con el tamaño del padding
            mask = np.zeros(cv_image_padded.shape[:2], np.uint8)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            
            # Definir rectángulo que abarca TODA la imagen original dentro del padding
            # El rectángulo es (x, y, w, h)
            height, width = cv_image.shape[:2]
            rect = (pad, pad, width, height)
            
            # Ejecutar GrabCut
            cv2.grabCut(cv_image_padded, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
            
            # Recuperar la máscara correspondiente a la imagen original (quitando padding)
            mask_padded = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            mask2 = mask_padded[pad:pad+height, pad:pad+width]
            
            # Aplicar dilatación y erosión para suavizar bordes
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Aplicar Gaussian Blur para suavizado de bordes
            mask2 = cv2.GaussianBlur(mask2, (5, 5), 0)
            
            # Normalizar máscara a rango 0-255
            mask2 = np.uint8(mask2 * 255)
            
            # Convertir imagen original a RGBA (usando la original cv_image)
            cv_image_rgba = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGBA)
            
            # Aplicar máscara al canal alfa
            cv_image_rgba[:, :, 3] = mask2
            
            # Crear imagen de salida
            output = Image.fromarray(cv_image_rgba)
            
            return output
            
        except Exception as e:
            print(f"Error en remove_background_opencv: {e}")
            # Si falla todo, devolver imagen original con alpha
            image_rgba = image.convert('RGBA')
            return image_rgba

class BackgroundRemoverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Eliminador de fondo")
        self.setWindowIcon(QIcon("favicon.ico"))
        
        # Configurar ventana: fixed, no maximizar, sin redimensión
        self.setFixedSize(900, 700)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        
        # Centrar ventana en pantalla
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2
        )
        
        # Cargar estilos desde archivo CSS
        self.load_stylesheet()

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Título
        title = QLabel("🎨 Eliminador de fondo")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # ===== GRUPO: ARCHIVO DE ORIGEN =====
        group_origen = QGroupBox("📁 Imagen de origen")
        group_origen.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout_origen = QVBoxLayout()
        
        layout_origen_h = QHBoxLayout()
        self.entry_origen = QLineEdit()
        self.entry_origen.setPlaceholderText("Selecciona la imagen de entrada")
        self.entry_origen.setReadOnly(True)
        button_origen = QPushButton("📂 Seleccionar")
        button_origen.setMinimumWidth(120)
        button_origen.clicked.connect(self.select_image)
        layout_origen_h.addWidget(self.entry_origen)
        layout_origen_h.addWidget(button_origen)
        layout_origen.addLayout(layout_origen_h)
        
        # Preview de imagen origen
        self.preview_origen = QLabel()
        self.preview_origen.setMinimumHeight(250)
        self.preview_origen.setMaximumHeight(250)
        self.preview_origen.setMaximumWidth(850)
        self.preview_origen.setStyleSheet("border: 2px dashed #3d5a78; border-radius: 5px; background-color: #f5f8fd;")
        self.preview_origen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_origen.setScaledContents(False)
        self.preview_origen.setText("📷 Preview aquí")
        layout_origen.addWidget(self.preview_origen)
        
        group_origen.setLayout(layout_origen)
        main_layout.addWidget(group_origen)

        # ===== GRUPO: OPCIONES DE PROCESAMIENTO =====
        group_opciones = QGroupBox("⚙️ Opciones de procesamiento")
        group_opciones.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout_opciones = QVBoxLayout()
        
        # Calidad
        layout_calidad = QHBoxLayout()
        layout_calidad.addWidget(QLabel("Calidad de guardado:"))
        self.slider_calidad = QSlider(Qt.Orientation.Horizontal)
        self.slider_calidad.setMinimum(1)
        self.slider_calidad.setMaximum(100)
        self.slider_calidad.setValue(95)
        self.slider_calidad.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_calidad.setTickInterval(10)
        self.label_calidad_valor = QLabel("95%")
        self.label_calidad_valor.setMinimumWidth(40)
        self.slider_calidad.sliderMoved.connect(self.update_calidad_label)
        self.slider_calidad.valueChanged.connect(self.update_calidad_label)
        layout_calidad.addWidget(self.slider_calidad)
        layout_calidad.addWidget(self.label_calidad_valor)
        layout_opciones.addLayout(layout_calidad)
        
        # Formato de salida
        layout_formato = QHBoxLayout()
        layout_formato.addWidget(QLabel("Formato de salida:"))
        self.combo_formato = QComboBox()
        self.combo_formato.addItems(["PNG (con transparencia)", "PNG (fondo blanco)", "PNG (fondo negro)", "JPEG"])
        layout_formato.addWidget(self.combo_formato)
        layout_formato.addStretch()
        layout_opciones.addLayout(layout_formato)
        
        # Opciones adicionales
        self.check_backup = QCheckBox("Hacer copia de seguridad del original")
        self.check_backup.setChecked(True)
        layout_opciones.addWidget(self.check_backup)
        
        group_opciones.setLayout(layout_opciones)
        main_layout.addWidget(group_opciones)

        # ===== GRUPO: ARCHIVO DE DESTINO =====
        group_destino = QGroupBox("")
        group_destino.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout_destino = QVBoxLayout()
        
        layout_destino_h = QHBoxLayout()
        self.entry_destino = QLineEdit()
        self.entry_destino.setPlaceholderText("Ruta y nombre del archivo de salida")
        button_examinar = QPushButton("🔎 Examinar")
        button_examinar.setMinimumWidth(100)
        button_examinar.clicked.connect(self.save_image)
        
        button_guardar = QPushButton("💾 Guardar")
        button_guardar.setMinimumWidth(100)
        button_guardar.clicked.connect(self.remove_background)
        
        layout_destino_h.addWidget(self.entry_destino)
        layout_destino_h.addWidget(button_examinar)
        layout_destino_h.addWidget(button_guardar)
        layout_destino.addLayout(layout_destino_h)
        
        group_destino.setLayout(layout_destino)
        main_layout.addWidget(group_destino)

        # ===== BARRA DE PROGRESO =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel()
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)

        # ===== BOTONES DE ACCIÓN =====
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(12)
        
        button_procesar = QPushButton("✨ Eliminar fondo")
        button_procesar.setObjectName("btnPrimary")
        button_procesar.setMinimumHeight(40)
        button_procesar.setMaximumWidth(160)
        button_procesar.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        button_procesar.clicked.connect(self.remove_background)
        
        button_limpiar = QPushButton("🔄 Limpiar")
        button_limpiar.setObjectName("btnSecondary")
        button_limpiar.setMinimumHeight(40)
        button_limpiar.setMaximumWidth(130)
        button_limpiar.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        button_limpiar.clicked.connect(self.clear_fields)
        
        button_abrir_carpeta = QPushButton("📂 Abrir carpeta")
        button_abrir_carpeta.setObjectName("btnSecondary")
        button_abrir_carpeta.setMinimumHeight(40)
        button_abrir_carpeta.setMaximumWidth(160)
        button_abrir_carpeta.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        button_abrir_carpeta.clicked.connect(self.open_output_folder)
        
        layout_botones.addStretch()
        layout_botones.addWidget(button_procesar)
        layout_botones.addWidget(button_limpiar)
        layout_botones.addWidget(button_abrir_carpeta)
        layout_botones.addStretch()
        
        main_layout.addLayout(layout_botones)

        central_widget.setLayout(main_layout)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona la imagen de origen",
            "",
            "Archivos de imagen (*.jpg *.jpeg *.png *.bmp *.gif);;Todos los archivos (*)"
        )
        if file_path:
            self.entry_origen.setText(file_path)
            self.update_preview(file_path)
            # Sugerir nombre de salida
            input_name = Path(file_path).stem
            output_path = str(Path(file_path).parent / f"{input_name}_sf.png")
            self.entry_destino.setText(output_path)

    def update_preview(self, image_path):
        try:
            img = Image.open(image_path)
            
            # Convertir a RGBA siempre para consistencia
            img = img.convert('RGBA')
            
            # Convertir a bytes para QImage
            data = img.tobytes("raw", "RGBA")
            q_image = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Definir dimensiones máximas seguras (un poco menos que el contenedor para margen)
            # Contenedor: 850x250
            # Margen seguro: 820x230
            max_w = 820
            max_h = 230
            
            # Escalar usando Qt (alta calidad y mantiene aspecto)
            scaled_pixmap = pixmap.scaled(
                max_w, max_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.preview_origen.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error al cargar preview: {e}")
            self.preview_origen.setText(f"❌ Error: {str(e)[:30]}")

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar imagen sin fondo",
            "",
            "Imagen PNG (*.png);;Imagen JPEG (*.jpg);;Todos los archivos (*)"
        )
        if file_path:
            self.entry_destino.setText(file_path)

    def remove_background(self):
        ruta_origen = self.entry_origen.text()
        ruta_destino = self.entry_destino.text()

        if not ruta_origen or not ruta_destino:
            QMessageBox.critical(self, "Error", 
                "Debes seleccionar tanto la ruta de origen como la de destino.")
            return

        if not os.path.exists(ruta_origen):
            QMessageBox.critical(self, "Error", 
                "La imagen de origen no existe.")
            return

        try:
            # Hacer backup si está activado
            if self.check_backup.isChecked() and os.path.exists(ruta_destino):
                backup_path = str(Path(ruta_destino).with_stem(Path(ruta_destino).stem + "_backup"))
                if not os.path.exists(backup_path):
                    import shutil
                    shutil.copy(ruta_destino, backup_path)

            # Procesar en thread separado
            self.progress_bar.setVisible(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setRange(0, 0) # Indeterminado al inicio
            
            calidad = self.slider_calidad.value()
            self.worker = RemoveBackgroundWorker(ruta_origen, ruta_destino, calidad)
            self.worker.finished.connect(self.on_process_finished)
            self.worker.error.connect(self.on_process_error)
            self.worker.progress.connect(self.update_status_text)
            self.worker.progress_value.connect(self.update_progress_value)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ha ocurrido un error: {e}")

    def on_process_finished(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_label.setText("✅ ¡Imagen procesada correctamente!")
        QMessageBox.information(self, "Éxito", 
            "La imagen ha sido procesada correctamente.\n\nArchivo guardado en:\n" + self.entry_destino.text())

    def on_process_error(self, error):
        self.progress_bar.setVisible(False)
        self.progress_label.setText(f"❌ Error: {error}")
        QMessageBox.critical(self, "Error", f"Error al procesar: {error}")

    def update_status_text(self, message):
        self.progress_label.setText(f"⏳ {message}")

    def update_progress_value(self, value):
        if value == -1:
            self.progress_bar.setRange(0, 0) # Indeterminado
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(value)

    def clear_fields(self):
        self.entry_origen.clear()
        self.entry_destino.clear()
        self.preview_origen.setText("📷 Preview aquí")
        self.progress_label.setText("")
        self.progress_bar.setVisible(False)

    def update_calidad_label(self):
        """Actualizar la etiqueta de calidad cuando cambia el slider"""
        valor = self.slider_calidad.value()
        self.label_calidad_valor.setText(f"{valor}%")

    def open_output_folder(self):
        ruta_destino = self.entry_destino.text()
        if ruta_destino and os.path.exists(ruta_destino):
            output_dir = str(Path(ruta_destino).parent)
            os.startfile(output_dir)
        else:
            QMessageBox.warning(self, "Advertencia", 
                "Debes guardar una imagen primero.")

    def load_stylesheet(self):
        """Cargar estilos desde archivo CSS externo"""
        try:
            css_file = os.path.join(os.path.dirname(__file__), 'styles.qss')
            with open(css_file, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error cargando estilos: {e}")
            # Fallback al estilo por defecto
            self.setStyleSheet(self.get_default_stylesheet())

    def get_default_stylesheet(self):
        """Estilos por defecto como fallback"""
        return """
            QMainWindow {
                background-color: #e8eef5;
            }
            QLabel {
                color: #1a1a1a;
                font-weight: bold;
            }
            QGroupBox {
                border: 2px solid #b0c4de;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #1a1a1a;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #1a1a1a;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #b0c4de;
                border-radius: 4px;
                background-color: white;
                color: #1a1a1a;
            }
            QLineEdit:focus {
                border: 2px solid #5b7a9d;
                color: #1a1a1a;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                color: #1a1a1a;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #b0c4de;
                border-radius: 4px;
                background-color: white;
                color: #1a1a1a;
            }
            QCheckBox {
                color: #1a1a1a;
                font-weight: bold;
                spacing: 5px;
            }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackgroundRemoverGUI()
    window.show()
    sys.exit(app.exec())
