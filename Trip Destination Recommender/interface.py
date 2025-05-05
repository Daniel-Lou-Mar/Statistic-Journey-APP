import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from functions import buscar_vuelos_y_hoteles
from predictive_model import predecir_viaje

# Interfaz gráfica
class InterfazConsultaVuelos:
    def __init__(self, root):
        self.root = root
        self.root.title("Trip request")
                
        tk.Label(root, text="Number of people:").grid(row=0, column=0)
        self.numero = tk.Entry(root)
        self.numero.grid(row=0, column=1)
        
        tk.Label(root, text="Minimum price:").grid(row=1, column=0)
        self.min = tk.Entry(root)
        self.min.grid(row=1, column=1)
        
        tk.Label(root, text="Maximun price:").grid(row=2, column=0)
        self.max = tk.Entry(root)
        self.max.grid(row=2, column=1)
        
        tk.Label(root, text="Departure (ex: Barcelona):").grid(row=3, column=0)
        self.dep = tk.Entry(root)
        self.dep.grid(row=3, column=1)
        
        tk.Label(root, text="Maximun distance:").grid(row=4, column=0)
        self.max_dist = tk.Entry(root)
        self.max_dist.grid(row=4, column=1)
        
        tk.Label(root, text="Departure Date (YYYY-MM-DD):").grid(row=5, column=0)
        self.dep_date = tk.Entry(root)
        self.dep_date.grid(row=5, column=1)
        
        tk.Label(root, text="Arrival Date (YYYY-MM-DD):").grid(row=6, column=0)
        self.arr_date = tk.Entry(root)
        self.arr_date.grid(row=6, column=1)
        
        
        tk.Label(root, text="Climate (tropical, dry, polar):").grid(row=7, column=0)
        self.climate = tk.Entry(root)
        self.climate.grid(row=7, column=1)
        tk.Button(root, text="Realizar Consulta", command=self.realizar_consulta).grid(row=9, column=0, columnspan=2)
    

    def realizar_consulta(self):
        num = self.numero.get().strip()
        min_price = self.min.get().strip()
        max_price = self.max.get().strip()
        dep = self.dep.get().strip()
        max_dist = self.max_dist.get().strip()
        dep_date = self.dep_date.get().strip()
        arr_date = self.arr_date.get().strip()
        climate = self.climate.get().strip().lower()

        if not num:
            messagebox.showerror("Error", "Debe indicar número de personas.")
            return

        try:
            # Llamada a la búsqueda
            resultados = buscar_vuelos_y_hoteles(
                int(num),
                float(min_price), float(max_price),
                float(max_dist),
                dep_date, arr_date,
                dep, climate,
            )
            if not resultados:
                messagebox.showinfo("Resultados", "No se encontraron opciones.")
                return

            # Calcular probabilidad para cada resultado
            opciones = []
            for r in resultados:
                pred = predecir_viaje(
                    per=int(num),
                    dis=r.get("distancia", 0),
                    din=r.get("precio", 0),
                    nativo_extranjero=r.get("nativo", 0),
                    preferencia_clima=r.get("clima", climate)
                )
                opciones.append({
                    "ciudad": r.get("ciudad", "N/A"),
                    "precio": r.get("precio", 0),
                    "destino": r.get("destino", "N/A"),
                    "prob": pred["probabilidad"]
                })

            # Ordenar y tomar top 3
            mejores = sorted(opciones, key=lambda x: x["prob"], reverse=True)[:3]

            # Construir mensaje
            texto = "Top 3 options:\n"
            for i, opt in enumerate(mejores, 1):
                texto += f"{i}. {opt["ciudad"]} ({opt["precio"]}€) – {opt['prob']*100:.1f}%\n"

            messagebox.showinfo("Best options", texto)

        except Exception as e:
            messagebox.showerror("Error", str(e))
