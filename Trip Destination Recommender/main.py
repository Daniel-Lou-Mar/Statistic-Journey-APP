import tkinter as tk
import functions
import interfaz
import predictive_model
from interfaz import InterfazConsultaVuelos

def preguntar_interfaz():
    root = tk.Tk()
    app = InterfazConsultaVuelos(root)
    root.mainloop()

preguntar_interfaz()