import tkinter as tk
from remover_fondo import BackgroundRemover

class GUI:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Eliminador de fondo de imágenes")
        self.ventana.resizable(0, 0)
        self.ancho = 620
        self.alto = 155
        self.ventana_x = ventana.winfo_screenwidth() // 2 - self.ancho // 2
        self.ventana_y = ventana.winfo_screenheight() // 2 - self.alto // 2
        posicion = str(self.ancho) + "x" + str(self.alto) + "+" + str(self.ventana_x) + "+" + str(self.ventana_y)
        self.ventana.geometry(posicion)

        self.logic = BackgroundRemover(self)

        self.label_origen = tk.Label(root, text="Ruta de la imagen de origen:")
        self.label_origen.grid(row=0, column=0, padx=10, pady=10)

        self.entry_origen = tk.Entry(root, width=50)
        self.entry_origen.grid(row=0, column=1, padx=10, pady=10)

        self.button_origen = tk.Button(root, text="Seleccionar", command=self.logic.select_image)
        self.button_origen.grid(row=0, column=2, padx=10, pady=10)

        self.label_destino = tk.Label(root, text="Ruta de la imagen de destino:")
        self.label_destino.grid(row=1, column=0, padx=10, pady=10)

        self.entry_destino = tk.Entry(root, width=50)
        self.entry_destino.grid(row=1, column=1, padx=10, pady=10)

        self.button_destino = tk.Button(root, text="Guardar como", command=self.logic.save_image)
        self.button_destino.grid(row=1, column=2, padx=10, pady=10)

        self.button_procesar = tk.Button(root, text="Eliminar fondo", command=self.logic.remove_background)
        self.button_procesar.grid(row=2, columnspan=3, pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()