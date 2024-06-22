import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from rembg import remove

class BackgroundRemover:
    
    def __init__(self, app):
        self.app = app

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona la imagen de origen",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")]
        )
        self.app.entry_origen.delete(0, tk.END)
        self.app.entry_origen.insert(0, file_path)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png")],
            title="Guardar imagen sin fondo"
        )
        self.app.entry_destino.delete(0, tk.END)
        self.app.entry_destino.insert(0, file_path)

    def remove_background(self):
        ruta_origen = self.app.entry_origen.get()
        ruta_destino = self.app.entry_destino.get()

        if not ruta_origen or not ruta_destino:
            messagebox.showerror("Error", "Debes seleccionar tanto la ruta de origen como la de destino.")
            return

        try:
            imagen_base = Image.open(ruta_origen)
            output = self.remove_background_logic(imagen_base)
            output.save(ruta_destino)
            messagebox.showinfo("Éxito", "Imagen procesada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

    def remove_background_logic(self, image):
        return remove(image)