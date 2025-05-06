import flet as ft
import datetime
from functions import buscar_vuelos_y_hoteles
from predictive_model import predecir_viaje

def main(page: ft.Page):
    page.title = "Trip request"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width = 600
    page.window.height = 700
    page.padding = 20


    status = ft.Text(color="red")


    numero_input = ft.TextField(label="Número de personas", width=200)


    budget_value = ft.Text("100 – 1000 €")
    def on_budget_change(e: ft.ControlEvent):
        budget_value.value = f"{e.control.start_value} – {e.control.end_value} €"
        page.update()

    budget_slider = ft.RangeSlider(
        label="Presupuesto (€)",
        min=0,
        max=5000,
        divisions=100,
        start_value=100,
        end_value=1000,
        on_change=on_budget_change,
        width=300,
    )

    dep_input      = ft.TextField(label="Salida (ej: Barcelona)", width=200)
    max_dist_input = ft.TextField(label="Distancia máxima (km)", width=200)

    dep_date_value = [None]
    arr_date_value = [None]

    dep_dp = ft.DatePicker(
        first_date=datetime.date(2020, 1, 1),
        last_date =datetime.date(2030, 12, 31),
        help_text="Selecciona fecha de salida"
    )
    arr_dp = ft.DatePicker(
        first_date=datetime.date(2020, 1, 1),
        last_date =datetime.date(2030, 12, 31),
        help_text="Selecciona fecha de llegada"
    )

    def on_dep_change(e: ft.ControlEvent):
        dep_date_value[0] = e.control.value
        dep_date_button.text = e.control.value.strftime("%Y-%m-%d")
        page.update()

    def on_arr_change(e: ft.ControlEvent):
        arr_date_value[0] = e.control.value
        arr_date_button.text = e.control.value.strftime("%Y-%m-%d")
        page.update()

    dep_dp.on_change = on_dep_change
    arr_dp.on_change = on_arr_change

    page.overlay.append(dep_dp)
    page.overlay.append(arr_dp)
    page.update()  

    dep_date_button = ft.ElevatedButton(
        text="Seleccionar fecha de salida",
        on_click=lambda e: page.open(dep_dp)
    )
    arr_date_button = ft.ElevatedButton(
        text="Seleccionar fecha de llegada",
        on_click=lambda e: page.open(arr_dp)
    )

    # Selector de clima
    climate_input = ft.Dropdown(
        label="Clima", width=200,
        options=[ft.dropdown.Option(c) for c in ("tropical", "dry", "polar")]
    )

    # Lógica de “Realizar Consulta”
    def realizar_consulta(e: ft.ControlEvent):
        status.value = ""
        page.update()
        try:
            # Leer y validar inputs
            num       = int(numero_input.value)
            min_price = budget_slider.start_value
            max_price = budget_slider.end_value
            dep_city  = dep_input.value.strip()
            max_dist  = float(max_dist_input.value)

            if not dep_date_value[0] or not arr_date_value[0]:
                status.value = "Debes seleccionar ambas fechas."
                page.update()
                return

            dep_date = dep_date_value[0].strftime("%Y-%m-%d")
            arr_date = arr_date_value[0].strftime("%Y-%m-%d")
            climate  = climate_input.value

            # Búsqueda de vuelos y hoteles
            resultados = buscar_vuelos_y_hoteles(
                num,
                min_price,
                max_price,
                max_dist,
                dep_date,
                arr_date,
                dep_city,
                climate,
            )

            # Si no hay resultados
            if not resultados:
                dlg = ft.AlertDialog(
                    title=ft.Text("Resultados"),
                    content=ft.Text("No se encontraron opciones."),
                )
                # Función para cerrar el diálogo
                def close_no_results(e):
                    dlg.open = False
                    page.update()
                dlg.actions = [ft.TextButton("Cerrar", on_click=close_no_results)]
                page.open(dlg)
                page.update()
                return

            # Calcular probabilidades y ordenar
            opciones = []
            for r in resultados:
                pred = predecir_viaje(
                    per=num,
                    dis=r.get("distancia", 0),
                    din=r.get("precio", 0),
                    nativo_extranjero=r.get("nativo", 0),
                    preferencia_clima=r.get("clima", climate)
                )
                opciones.append({
                    "ciudad": r.get("ciudad", "N/A"),
                    "precio": r.get("precio", 0),
                    "prob": pred["probabilidad"]
                })

            mejores = sorted(opciones, key=lambda x: x["prob"], reverse=True)[:3]
            texto = "\n".join(
                f"{i+1}. {opt['ciudad']} ({opt['precio']}€) – {opt['prob']*100:.1f}%"
                for i, opt in enumerate(mejores)
            )

            # Mostrar diálogo con las top 3 opciones
            dlg = ft.AlertDialog(
                title=ft.Text("Top 3 opciones"),
                content=ft.Text(texto),
            )
            def close_results(e):
                dlg.open = False
                page.update()
            dlg.actions = [ft.TextButton("Cerrar", on_click=close_results)]
            page.open(dlg)
            page.update()

        except Exception as ex:
            status.value = f"Error: {ex}"
            page.update()

    consulta_button = ft.ElevatedButton("Realizar Consulta", on_click=realizar_consulta)

    # Montamos todo en la página
    page.add(
        ft.Text("Trip Destination Recommender", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        status,
        numero_input,
        ft.Row([ft.Text("Presupuesto (€):"), budget_slider]),
        budget_value,
        dep_input,
        ft.Text("Introduce las fechas de salida y llegada:"),
        ft.Row([dep_date_button, arr_date_button],
               alignment=ft.MainAxisAlignment.CENTER,
               spacing=10),
        max_dist_input,
        climate_input,
        consulta_button
    )

if __name__ == "__main__":
    ft.app(target=main)
