"""Laboratorio didáctico, beta 0.2. Ejecutar: streamlit run app.py."""
import pandas as pd
import streamlit as st

from simulador_macroeconomia import Politica, simular

TITULO = "Laboratorio Macroeconómico Argentino - UTN.BA"
st.set_page_config(page_title=TITULO, layout="wide")
st.title(TITULO)
st.markdown("**Cátedra: Política Económica**")
st.caption("🧪 Versión beta 0.2 — en prueba y mejora")
st.caption("Simulador exclusivamente para uso didáctico. Parámetros ilustrativos y con fines educativos; no es un pronóstico.")

with st.sidebar:
    st.header("Políticas sostenidas desde el año 1")
    gasto = st.slider("Cambio en gasto público (puntos del PIB)", -5.0, 5.0, 0.0, 0.5)
    impuestos = st.slider("Cambio en presión tributaria (puntos del PIB)", -5.0, 5.0, 0.0, 0.5)
    tasa = st.slider("Cambio en tasa nominal (puntos porcentuales)", -10.0, 10.0, 0.0, 0.5)
    emision = st.slider("Emisión adicional (puntos de crecimiento monetario)", -15.0, 15.0, 0.0, 0.5)
    periodos = st.slider("Años", 2, 15, 8)

politica = Politica(gasto, impuestos, tasa, emision)
base = pd.DataFrame(simular(Politica(), periodos)).set_index("anio")
escenario = pd.DataFrame(simular(politica, periodos)).set_index("anio")
etiquetas = {
    "pib": "PIB real (índice)", "crecimiento": "Crecimiento del PIB real (%)",
    "inflacion": "Inflación anual (%)", "desempleo": "Desempleo (%)",
    "deficit": "Déficit fiscal (% PIB)", "deuda": "Deuda pública (% PIB)",
    "reservas": "Reservas (índice)",
}
columnas = list(etiquetas)

st.caption(f"Los indicadores muestran el año {periodos}. Las diferencias comparan con el escenario sin cambios.")
for fila in (columnas[:4], columnas[4:]):
    for col, nombre in zip(st.columns(len(fila)), fila):
        diferencia = escenario[nombre].iloc[-1] - base[nombre].iloc[-1]
        unidad = "puntos de índice" if nombre in ("pib", "reservas") else "pp"
        col.metric(
            etiquetas[nombre], f"{escenario[nombre].iloc[-1]:.2f}",
            f"{diferencia:+.2f} {unidad} vs. base",
            delta_color="off",
        )

for fila in (("pib", "crecimiento"), ("inflacion", "desempleo"), ("deficit", "deuda", "reservas")):
    for col, nombre in zip(st.columns(len(fila)), fila):
        with col:
            st.subheader(etiquetas[nombre])
            datos = pd.DataFrame({"Escenario": escenario[nombre], "Sin cambios": base[nombre]})
            if nombre == "crecimiento":
                datos = datos.loc[1:]
            st.line_chart(datos)

st.caption("PIB y reservas: índices con año 0 = 100. El crecimiento se calcula desde el año 1. Un déficit negativo representa superávit.")
st.subheader("Lectura del escenario")

if politica == Politica():
    st.write("Elegí una o más políticas para comparar sus efectos con la trayectoria sin cambios.")
    st.write("El PIB real crece 2% anual en la referencia. Déficit y deuda pueden aumentar aunque no cambies controles: la referencia ya parte de un déficit fiscal.")
else:
    st.markdown("**Políticas elegidas y mecanismos del modelo**")
    if gasto:
        st.write("• " + (
            "El mayor gasto público impulsa la demanda y aumenta el gasto fiscal. La actividad recupera parte de la recaudación, pero no necesariamente compensa ese costo."
            if gasto > 0 else
            "El menor gasto público reduce la demanda y el gasto fiscal. La menor actividad también reduce parte de la recaudación y atenúa el ahorro fiscal."
        ))
    if impuestos:
        st.write("• " + (
            "La mayor carga tributaria reduce el impulso a la demanda y mejora directamente la recaudación. El efecto final incorpora también la respuesta de la actividad."
            if impuestos > 0 else
            "La menor carga tributaria impulsa la demanda y reduce la recaudación directa. El crecimiento recupera parte de esa recaudación; su efecto neto se observa en el déficit y la deuda."
        ))
    if tasa:
        st.write("• " + (
            "La tasa más alta reduce el impulso a la actividad y la inflación. En esta formulación también sostiene directamente el índice de reservas."
            if tasa > 0 else
            "La tasa más baja impulsa la actividad y añade presión sobre la inflación. En esta formulación también reduce directamente el índice de reservas."
        ))
    if emision:
        st.write("• " + (
            "La mayor emisión impulsa inicialmente la demanda, eleva la presión inflacionaria y reduce directamente el índice de reservas."
            if emision > 0 else
            "La menor emisión reduce el impulso a la demanda y la presión inflacionaria, y sostiene directamente el índice de reservas."
        ))
    if sum(v != 0 for v in (gasto, impuestos, tasa, emision)) > 1:
        st.write("Combinaste políticas: sus efectos pueden reforzarse o compensarse. Las cifras siguientes muestran el resultado conjunto.")

causas = {
    "pib": "El nivel del PIB acumula las tasas de crecimiento de cada año. Puede seguir aumentando mientras su crecimiento se desacelera.",
    "crecimiento": "Es la variación del PIB respecto del año anterior. Responde al impulso conjunto de las políticas, que se atenúa con el tiempo, y a la penalización que el modelo asigna a la inflación por encima de 25%.",
    "inflacion": "Ajusta gradualmente y responde a la emisión, la tasa y la demanda. La rebaja tributaria tiene además un efecto específico supuesto en esta ecuación.",
    "desempleo": "Responde al crecimiento respecto de la tendencia de 2%: crecer más reduce desempleo y crecer menos lo aumenta. El empleo puede deteriorarse incluso con un PIB que todavía crece.",
    "deficit": "Es un flujo anual. Incorpora gasto, impuestos, recaudación ligada al crecimiento y un ajuste simplificado de costos financieros ligado a la deuda heredada.",
    "deuda": "Es un stock acumulado expresado como porcentaje del PIB. El déficit agrega deuda; el crecimiento reduce el peso de la deuda heredada en relación con el PIB. Por eso la deuda/PIB puede bajar aunque haya déficit, si el efecto del crecimiento lo compensa.",
    "reservas": "El índice responde a los efectos supuestos de tasa, emisión, demanda y déficit. Todavía no representa compras y ventas de divisas ni un régimen cambiario explícito.",
}

st.markdown("**Resultados y explicación por variable**")
for nombre in columnas:
    st.markdown(f"**{etiquetas[nombre]}**")
    st.write(causas[nombre])
    if politica != Politica():
        d1 = escenario.loc[1, nombre] - base.loc[1, nombre]
        dn = escenario.loc[periodos, nombre] - base.loc[periodos, nombre]
        unidad = "puntos de índice" if nombre in ("pib", "reservas") else "puntos porcentuales"
        comparacion = ("prácticamente coincide con la referencia" if abs(dn) < 0.005
                       else "queda por encima de la referencia" if dn > 0
                       else "queda por debajo de la referencia")
        st.write(f"Año 1: diferencia de {d1:+.2f} {unidad}. Año {periodos}: diferencia de {dn:+.2f} {unidad}; {comparacion}.")
    if nombre == "crecimiento":
        valor = escenario.loc[periodos, nombre]
        lectura = "contracción" if valor < -0.005 else "actividad prácticamente estable" if abs(valor) < 0.005 else "expansión"
        st.write(f"En el año {periodos}, el PIB varía {valor:+.2f}% respecto del año anterior: {lectura}.")
    if nombre == "deuda":
        cambio = escenario.loc[periodos, nombre] - escenario.loc[0, nombre]
        st.write(f"La deuda parte de 60% del PIB y termina en {escenario.loc[periodos, nombre]:.2f}%: cambio de {cambio:+.2f} puntos porcentuales respecto del año 0.")
        st.caption("Supuesto de esta beta: principal de la deuda ajustado por inflación y déficit global financiado con deuda. La emisión es un instrumento independiente; no se descuenta automáticamente del endeudamiento.")

if (escenario["reservas"] == 0).any():
    st.warning("El índice de reservas alcanza el piso de cero. El modelo no simula la crisis o el cambio de políticas que podría seguir a ese agotamiento.")
st.caption("La explicación describe las relaciones de este modelo didáctico. Los parámetros son ilustrativos y no estiman efectos para Argentina.")

with st.expander("Supuestos y límites del modelo"):
    st.markdown("""
- Año 0: PIB y reservas = 100; inflación = 25%, desempleo = 8%, déficit = 3% del PIB y deuda = 60% del PIB. **No son datos argentinos actuales**.
- El crecimiento del año 0 no se muestra: no contamos con un PIB del año anterior para calcularlo.
- Crecimiento tendencial = 2% anual. El impulso a la demanda se atenúa 28% cada año. La inflación es inercial y el desempleo responde al crecimiento.
- Gasto e impuestos se expresan como cambios sostenidos en puntos del PIB. El déficit incluye un ajuste financiero estilizado; no es exclusivamente déficit primario.
- La deuda heredada se ajusta por inflación. En la relación deuda/PIB ese ajuste se cancela con el crecimiento de precios del denominador. El déficit global agrega endeudamiento a valor corriente; no se suman intereses una segunda vez.
- Toda la necesidad de financiamiento fiscal se cubre con deuda. La emisión es un instrumento monetario independiente. No hay deuda en moneda extranjera, reestructuraciones ni otros ajustes de valuación. La deuda tiene piso cero; no se acumulan activos si un superávit supera el stock.
- No hay tipo de cambio, expectativas, restricciones de financiamiento, shocks externos ni calibración econométrica. La inflación se usa como aproximación del crecimiento del deflactor del PIB para el supuesto de indexación.
- **Cambio en beta 0.2:** se reemplazó la regla de deuda. Por su relación con el déficit y las reservas, los resultados pueden diferir de la versión inicial y de su guía docente.
""")
    st.code("""impulso = 0.85·Δgasto - 0.55·Δimpuestos - 0.22·Δtasa + 0.12·Δemisión
brecha(t) = impulso·0.72^(t-1)
crecimiento(t) = 2 + 0.55·brecha(t) - 0.05·máx(inflación(t-1)-25, 0)
PIB(t) = PIB(t-1)·[1 + crecimiento(t)/100]
desempleo(t) = desempleo(t-1) - 0.30·[crecimiento(t)-2] (piso 2%, techo 30%)
inflación(t) = máx(0, 0.70·inflación(t-1) + 0.30·[25 + 0.65·Δemisión + 0.55·brecha(t) - 0.45·Δtasa + 0.20·máx(-Δimpuestos, 0)])
déficit(t) = 3 + Δgasto - Δimpuestos - 0.20·[crecimiento(t)-2] + 0.025·[deuda(t-1)-60]
deuda(t) = máx(0, deuda(t-1)/[1 + crecimiento(t)/100] + déficit(t))
reservas(t) = máx(0, reservas(t-1) + 1 + 0.5·Δtasa - 0.8·Δemisión - 0.6·máx(brecha(t), 0) - 0.30·máx(déficit(t)-3, 0))""", language="text")

with st.expander("Tabla de resultados"):
    st.dataframe(escenario[columnas].rename(columns=etiquetas).round(2))
st.download_button("Descargar escenario CSV", escenario.round(3).to_csv().encode("utf-8-sig"),
                   "escenario_macroeconomico.csv", "text/csv")
