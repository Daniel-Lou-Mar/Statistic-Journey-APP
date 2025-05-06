import pandas as pd
import os
import statsmodels.formula.api as smf

# 1) Carga los datos (ajusta la ruta para que sea relativa al módulo actual)
ruta_base = os.path.join(os.path.dirname(__file__), "viajes.csv")
df = pd.read_csv(ruta_base)

# 2) Entrena el modelo logit con la misma fórmula
modelo = smf.logit(
    "admit ~ per + dis + din + nativo_extranjero + preferencia_clima",
    data=df
).fit(disp=False)

# 3) Función de predicción
def predecir_viaje(per, dis, din, nativo_extranjero, preferencia_clima):
    nuevo = pd.DataFrame([{
        "per": per,
        "dis": dis,
        "din": din,
        "nativo_extranjero": nativo_extranjero,
        "preferencia_clima": preferencia_clima
    }])
    prob = modelo.predict(nuevo)[0]
    decision = "SI" if prob >= 0.5 else "NO"
    return {"probabilidad": float(prob), "decision": decision}
