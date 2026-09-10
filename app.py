import math
import streamlit as st

st.set_page_config(page_title="Calculadora de Hendido", layout="wide")

st.title("🛠️ Especificaciones de Troquelado: Steel Counterplate")
st.caption("Cálculo de matrices, profundidades y reglas de marcado (Regla 2PT / 0.71 mm)")

# Entrada interactiva de Streamlit (reemplaza a input())
espesor = st.number_input(
    "Ingrese el espesor del cartón (s) en mm:", 
    min_value=0.10, 
    max_value=1.50, 
    value=0.40, 
    step=0.01
)

def calcular_parametros(s):
    regla_espesor = 0.71  # 2PT

    # 1. SHOP FLOOR (Regla Fija 23.80 mm en Steel 1.00 mm)
    sf_profundidad = round(math.ceil((s + 0.10) * 20) / 20, 2)
    sf_ancho_par = round(regla_espesor + (1.60 * s), 2)
    sf_ancho_cross = round(regla_espesor + (1.85 * s), 2)
    sf_ancho_unico = round(math.ceil(sf_ancho_cross * 20) / 20, 2)

    # 2. MARBACH SPEC (Regla Rebajada)
    mb_profundidad = round(s + 0.05, 2)
    if s <= 0.35:
        mb_regla_altura = 23.60
    elif s <= 0.50:
        mb_regla_altura = 23.65
    else:
        mb_regla_altura = 23.70
        
    mb_ancho_par = round(regla_espesor + (1.50 * s), 2)
    mb_ancho_cross = round(regla_espesor + (1.75 * s), 2)
    mb_ancho_unico = round(math.ceil(mb_ancho_cross * 20) / 20, 2)

    # 3. PERTINAX TRADICIONAL
    pt_profundidad = round(s, 2)
    pt_regla_altura = round(23.80 - pt_profundidad, 2)
    pt_ancho_par = round(regla_espesor + (1.40 * s), 2)
    pt_ancho_cross = round(regla_espesor + (1.60 * s), 2)
    pt_ancho_unico = round(math.ceil(pt_ancho_cross * 20) / 20, 2)

    return {
        "1. Shop Floor (Estrategia Taller)": {
            "Regla Altura": "23.80 mm (FIJA)",
            "Chapa": "1.00 mm",
            "Profundidad (D)": f"{sf_profundidad:.2f} mm",
            "Ancho A Favor": f"{sf_ancho_par:.2f} mm",
            "Ancho A Contra": f"{sf_ancho_cross:.2f} mm",
            "Ancho Unificado Seguro": f"{sf_ancho_unico:.2f} mm",
            "Nota": "Regla fija de 23.80 mm. Máxima tolerancia operativa y seguridad."
        },
        "2. Marbach Spec": {
            "Regla Altura": f"{mb_regla_altura:.2f} mm (REBAJADA)",
            "Chapa": "1.00 mm",
            "Profundidad (D)": f"{mb_profundidad:.2f} mm",
            "Ancho A Favor": f"{mb_ancho_par:.2f} mm",
            "Ancho A Contra": f"{mb_ancho_cross:.2f} mm",
            "Ancho Unificado Seguro": f"{mb_ancho_unico:.2f} mm",
            "Nota": "Ajuste teórico estrecho para alta velocidad. Requiere regla rebajada."
        },
        "3. Pertinax Tradicional": {
            "Regla Altura": f"{pt_regla_altura:.2f} mm",
            "Chapa": "Matriz / Tira",
            "Profundidad (D)": f"{pt_profundidad:.2f} mm",
            "Ancho A Favor": f"{pt_ancho_par:.2f} mm",
            "Ancho A Contra": f"{pt_ancho_cross:.2f} mm",
            "Ancho Unificado Seguro": f"{pt_ancho_unico:.2f} mm",
            "Nota": "Referencia estándar. Altura de regla variable (23.80 - D)."
        }
    }

res = calcular_parametros(espesor)
cols = st.columns(3)

for idx, (perfil, datos) in enumerate(res.items()):
    with cols[idx]:
        st.subheader(perfil)
        st.metric("Altura de Regla", datos["Regla Altura"])
        st.write(f"**Profundidad Canal:** {datos['Profundidad (D)']}")
        st.write(f"**Ancho A Favor:** {datos['Ancho A Favor']}")
        st.write(f"**Ancho A Contra:** {datos['Ancho A Contra']}")
        st.write(f"**Ancho Unificado:** {datos['Ancho Unificado Seguro']}")
        st.info(datos["Nota"])
