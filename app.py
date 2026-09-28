"""Ejecutar con: streamlit run app.py"""
import pandas as pd
import streamlit as st

from simulador_macroeconomia import Politica, simular

st.set_page_config(page_title="Laboratorio Macroeconómico Argentino", layout="wide")
st.title("Laboratorio Macroeconómico Argentino")
st.caption("Simulador exclusivamente para uso didáctico. Parámetros ilustrativos y con fines educativos; no es un pronóstico.")

with st.sidebar:
    st.header("Políticas sostenidas desde el año 1")
    gasto = st.slider("Cambio en gasto público (% del PIB inicial)", -5.0, 5.0, 0.0, 0.5)
    impuestos = st.slider("Cambio en presión tributaria (puntos del PIB)", -5.0, 5.0, 0.0, 0.5)
    tasa = st.slider("Cambio en tasa nominal (puntos porcentuales)", -10.0, 10.0, 0.0, 0.5)
    emision = st.slider("Emisión adicional (puntos de crecimiento monetario)", -15.0, 15.0, 0.0, 0.5)
    periodos = st.slider("Años", 2, 15, 8)

politica = Politica(gasto, impuestos, tasa, emision)
base = pd.DataFrame(simular(Politica(), periodos)).set_index("anio")
escenario = pd.DataFrame(simular(politica, periodos)).set_index("anio")

columnas = ["pib", "inflacion", "desempleo", "deficit", "reservas"]
etiquetas = {"pib": "PIB real (índice)", "inflacion": "Inflación anual (%)",
             "desempleo": "Desempleo (%)", "deficit": "Déficit fiscal (% PIB)",
             "reservas": "Reservas (índice)"}
cols = st.columns(5)
for col, nombre in zip(cols, columnas):
    col.metric(etiquetas[nombre], f"{escenario[nombre].iloc[-1]:.1f}",
               f"{escenario[nombre].iloc[-1] - base[nombre].iloc[-1]:+.1f} vs. base")

for fila in (columnas[:3], columnas[3:]):
    cols = st.columns(len(fila))
    for col, nombre in zip(cols, fila):
        with col:
            st.subheader(etiquetas[nombre])
            st.line_chart(pd.DataFrame({"Escenario": escenario[nombre],
                                        "Sin cambios": base[nombre]}))

st.subheader("Lectura del escenario")
explicaciones = []
if gasto: explicaciones.append("El gasto impulsa la demanda y aumenta el déficit." if gasto > 0 else "El menor gasto reduce demanda y déficit.")
if impuestos: explicaciones.append("Más impuestos reducen consumo y déficit." if impuestos > 0 else "Menos impuestos estimulan demanda y elevan déficit.")
if tasa: explicaciones.append("La tasa más alta enfría actividad e inflación y sostiene reservas." if tasa > 0 else "La tasa más baja estimula actividad y presiona inflación y reservas.")
if emision: explicaciones.append("Más emisión estimula actividad inicialmente, eleva inflación y presiona reservas." if emision > 0 else "Menos emisión modera inflación y limita el impulso a la actividad.")
st.write(" ".join(explicaciones) if explicaciones else "Elegí una política para comparar con la trayectoria sin cambios.")

with st.expander("Supuestos y límites del modelo"):
    st.markdown("""- Año 0: PIB y reservas = 100 (índices); inflación = 25%, desempleo = 8%, déficit = 3% del PIB. Estos valores **no son datos argentinos actuales**.
- Crecimiento tendencial = 2% anual. El impulso a la demanda se atenúa 28% cada año; inflación ajusta gradualmente. El desempleo responde al crecimiento (regla tipo Okun).
- El déficit incorpora gasto, impuestos, recaudación ligada al crecimiento y deuda. Las reservas reflejan presiones estilizadas de tasa, emisión, demanda y déficit.
- No hay tipo de cambio explícito, expectativas racionales, restricciones de financiamiento, shocks externos ni estimación econométrica. Las magnitudes dependen de coeficientes elegidos para enseñanza; no permiten evaluar políticas reales.""")
    st.code("""brecha = (0.85·Δgasto − 0.55·Δimpuestos − 0.22·Δtasa + 0.12·Δemisión)·0.72^(año−1)
crecimiento = 2 + 0.55·brecha − 0.05·máx(inflación−25, 0)
desempleo(t) = desempleo(t−1) − 0.30·(crecimiento−2)
inflación(t) = 0.70·inflación(t−1) + 0.30·[25 + 0.65·Δemisión + 0.55·brecha − 0.45·Δtasa + 0.20·máx(−Δimpuestos, 0)]
déficit = 3 + Δgasto − Δimpuestos − 0.20·(crecimiento−2) + 0.025·(deuda−60)
reservas(t) = máx(0, reservas(t−1) + 1 + 0.5·Δtasa − 0.8·Δemisión − 0.6·máx(brecha, 0) − 0.30·máx(déficit−3, 0))""", language="text")

st.download_button("Descargar escenario CSV", escenario.round(3).to_csv().encode("utf-8-sig"),
                   "escenario_macroeconomico.csv", "text/csv")
