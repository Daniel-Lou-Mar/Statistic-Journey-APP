import tkinter as tk
import functions
import interface
import predictive_model
from interface import InterfazConsultaVuelos

def preguntar_interfaz():
    root = tk.Tk()
    app = InterfazConsultaVuelos(root)
    root.mainloop()

preguntar_interfaz()