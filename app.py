"""Laboratorio didáctico, beta 0.3. Ejecutar: streamlit run app.py."""
import pandas as pd
import streamlit as st

import simulador_macroeconomia as modelo
from simulador_macroeconomia import Politica, simular

TITULO = "Laboratorio Macroeconómico Argentino - UTN.BA"
st.set_page_config(page_title=TITULO, layout="wide")
st.title(TITULO)
st.markdown("**Cátedra: Política Económica**")
st.caption("🧪 Versión beta 0.3 — en prueba y mejora")
st.caption("Última actualización: 26/11/2026")
st.caption("Simulador exclusivamente para uso didáctico. Parámetros ilustrativos y con fines educativos; no es un pronóstico.")

if getattr(modelo, "VERSION_MODELO", None) != "0.3":
    st.error("Los dos archivos corresponden a versiones distintas. Reemplazá también simulador_macroeconomia.py por el archivo de la beta 0.3 y reiniciá la app desde Streamlit Cloud (Reboot app).")
    st.stop()

with st.sidebar:
    st.header("Régimen cambiario")
    regimen = st.radio("Tipo de cambio", ("Flexible", "Fijo"))
    st.caption("Flexible: flotación pura, sin intervención. Fijo: paridad inicial de 100; el Banco Central compra o vende reservas para defenderla.")
    st.header("Políticas sostenidas desde el año 1")
    gasto = st.slider("Cambio en gasto público (puntos del PIB)", -5.0, 5.0, 0.0, 0.5)
    impuestos = st.slider("Cambio en presión tributaria (puntos del PIB)", -5.0, 5.0, 0.0, 0.5)
    tasa = st.slider("Cambio en tasa nominal (puntos porcentuales)", -10.0, 10.0, 0.0, 0.5)
    emision = st.slider("Emisión adicional (puntos de crecimiento monetario)", -15.0, 15.0, 0.0, 0.5)
    periodos = st.slider("Años", 2, 15, 8)

politica = Politica(gasto, impuestos, tasa, emision, regimen)
referencia = Politica(regimen=regimen)
base = pd.DataFrame(simular(referencia, periodos)).set_index("anio")
escenario = pd.DataFrame(simular(politica, periodos)).set_index("anio")
etiquetas = {
    "pib": "PIB real (índice)", "crecimiento": "Crecimiento del PIB real (%)",
    "inflacion": "Inflación anual (%)", "desempleo": "Desempleo (%)",
    "deficit": "Déficit fiscal (% PIB)", "deuda": "Deuda pública (% PIB)",
    "reservas": "Reservas (índice)",
    "tc_nominal": "Tipo de cambio nominal (índice)",
    "tc_real": "Tipo de cambio real (índice)",
}
columnas = list(etiquetas)

st.caption(f"Los indicadores muestran el año {periodos}. Las diferencias comparan con el escenario sin cambios de políticas, bajo el mismo régimen cambiario.")
for fila in (columnas[:3], columnas[3:6], columnas[6:]):
    for col, nombre in zip(st.columns(len(fila)), fila):
        diferencia = escenario[nombre].iloc[-1] - base[nombre].iloc[-1]
        unidad = "puntos de índice" if nombre in ("pib", "reservas", "tc_nominal", "tc_real") else "pp"
        col.metric(
            etiquetas[nombre], f"{escenario[nombre].iloc[-1]:.2f}",
            f"{diferencia:+.2f} {unidad} vs. base",
            delta_color="off",
        )

for fila in (("pib", "crecimiento"), ("inflacion", "desempleo"), ("deficit", "deuda", "reservas"), ("tc_nominal", "tc_real")):
    for col, nombre in zip(st.columns(len(fila)), fila):
        with col:
            st.subheader(etiquetas[nombre])
            datos = pd.DataFrame({"Escenario": escenario[nombre], "Sin cambios": base[nombre]})
            if nombre == "crecimiento":
                datos = datos.loc[1:]
            st.line_chart(datos)

st.caption("PIB, reservas y tipos de cambio: índices con año 0 = 100, no cotizaciones en $/USD. Un tipo de cambio nominal mayor significa depreciación del peso; uno real mayor, depreciación real. Déficit negativo = superávit.")
if st.checkbox("Comparar los dos regímenes con las mismas políticas"):
    otro_regimen = "Fijo" if regimen == "Flexible" else "Flexible"
    otra = pd.DataFrame(simular(Politica(gasto, impuestos, tasa, emision, otro_regimen), periodos)).set_index("anio")
    st.caption("Esta comparación mantiene las cuatro políticas y cambia solamente el régimen inicial. Si el fijo agota reservas, pasa a flotación.")
    for col, nombre in zip(st.columns(2), ("tc_nominal", "reservas")):
        with col:
            st.subheader(etiquetas[nombre] + " por régimen")
            st.line_chart(pd.DataFrame({regimen: escenario[nombre], otro_regimen: otra[nombre]}))
st.subheader("Lectura del escenario")

if politica == referencia:
    st.write("Elegí una o más políticas para comparar sus efectos con la trayectoria sin cambios.")
    st.write("La referencia también depende del régimen: con flotación, parte de un crecimiento de 2%; con paridad fija, la apreciación real puede frenar la actividad. Déficit y deuda pueden aumentar aunque no cambies controles porque se parte de un déficit fiscal.")
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
            "La tasa más alta reduce el impulso a la actividad y la inflación. También reduce la presión de depreciación: con fijo puede reducir ventas de reservas y con flexible modera la suba de la cotización."
            if tasa > 0 else
            "La tasa más baja impulsa la actividad y añade presión sobre la inflación. También aumenta la presión de depreciación, que se refleja en reservas con fijo o en la cotización con flexible."
        ))
    if emision:
        st.write("• " + (
            "La mayor emisión impulsa inicialmente la demanda, eleva la presión inflacionaria y cambiaria: con fijo exige mayores ventas de reservas y con flexible presiona sobre la cotización."
            if emision > 0 else
            "La menor emisión reduce el impulso a la demanda y la presión inflacionaria, y alivia la presión cambiaria, con efectos sobre reservas o cotización según el régimen."
        ))
    if sum(v != 0 for v in (gasto, impuestos, tasa, emision)) > 1:
        st.write("Combinaste políticas: sus efectos pueden reforzarse o compensarse. Las cifras siguientes muestran el resultado conjunto.")

causas = {
    "pib": "El nivel del PIB acumula las tasas de crecimiento de cada año. Puede seguir aumentando mientras su crecimiento se desacelera.",
    "crecimiento": "Es la variación del PIB respecto del año anterior. Responde al impulso conjunto de las políticas, que se atenúa con el tiempo, al tipo de cambio real del año anterior y a la penalización que el modelo asigna a la inflación por encima de 25%.",
    "inflacion": "Ajusta gradualmente y responde a la emisión, la tasa y la demanda. Incluye un traslado parcial de la depreciación a los precios. La rebaja tributaria tiene además un efecto específico supuesto en esta ecuación.",
    "desempleo": "Responde al crecimiento respecto de la tendencia de 2%: crecer más reduce desempleo y crecer menos lo aumenta. El empleo puede deteriorarse incluso con un PIB que todavía crece.",
    "deficit": "Es un flujo anual. Incorpora gasto, impuestos, recaudación ligada al crecimiento y un ajuste simplificado de costos financieros ligado a la deuda heredada.",
    "deuda": "Es un stock acumulado expresado como porcentaje del PIB. El déficit agrega deuda; el crecimiento reduce el peso de la deuda heredada en relación con el PIB. Por eso la deuda/PIB puede bajar aunque haya déficit, si el efecto del crecimiento lo compensa.",
    "reservas": "Varía únicamente por la intervención cambiaria: compras lo aumentan y ventas lo reducen. En flotación pura queda constante. El índice no expresa dólares ni incluye valuaciones o rendimientos de activos.",
    "tc_nominal": "Mide la cotización en pesos por divisa como índice. Con fijo se mantiene en 100 mientras hay reservas para defenderlo; con flexible responde a la presión cambiaria.",
    "tc_real": "Se calcula como tipo de cambio nominal por precios externos dividido por precios locales, con base 100. Una caída representa apreciación real y resta impulso comercial al crecimiento del año siguiente. No mide por sí solo toda la competitividad.",
}

st.markdown("**Canal cambiario**")
if regimen == "Fijo":
    st.write("El Banco Central intenta sostener la paridad nominal inicial. Si la presión es de depreciación, vende reservas; si es de apreciación, compra. Una inflación local mayor que la externa aprecia el tipo de cambio real y reduce el impulso comercial a la actividad en el año siguiente. Al agotarse las reservas, esta beta abandona la paridad y pasa a flotación.")
else:
    st.write("La cotización responde a la presión del mercado sin compras ni ventas del Banco Central: por eso las reservas permanecen constantes en esta flotación pura. La depreciación incide sobre precios; la variación real depende también de la inflación local y externa.")
st.write("La presión cambiaria combina inflación previa, emisión, demanda, tasa local, déficit heredado y tipo de cambio real. Todavía no hay un mercado de capitales explícito ni tasa internacional; estos canales se incorporarán en otra etapa.")
st.markdown("**Resultados y explicación por variable**")
for nombre in columnas:
    st.markdown(f"**{etiquetas[nombre]}**")
    st.write(causas[nombre])
    if politica != referencia:
        d1 = escenario.loc[1, nombre] - base.loc[1, nombre]
        dn = escenario.loc[periodos, nombre] - base.loc[periodos, nombre]
        unidad = "puntos de índice" if nombre in ("pib", "reservas", "tc_nominal", "tc_real") else "puntos porcentuales"
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

for nombre_serie, datos_serie in (("escenario elegido", escenario), ("referencia sin cambios", base)):
    agotamiento = datos_serie.index[datos_serie["abandono_fijo"]]
    if len(agotamiento):
        st.warning(f"En el {nombre_serie}, las reservas se agotan en el año {agotamiento[0]}. El modelo abandona la paridad y pasa a flotación desde ese año. No simula default, controles de capitales ni una crisis bancaria.")
st.caption("La explicación describe las relaciones de este modelo didáctico. Los parámetros son ilustrativos y no estiman efectos para Argentina.")

with st.expander("Supuestos y límites del modelo"):
    st.markdown("""
- Año 0: PIB, reservas, tipo de cambio nominal y real = 100; inflación = 25%, desempleo = 8%, déficit = 3% del PIB y deuda = 60% del PIB. **Son valores ilustrativos, no datos argentinos actuales.**
- La referencia usa el mismo régimen inicial y las cuatro políticas en cero. Comparar regímenes conserva las políticas y cambia el régimen inicial.
- Inflación externa constante: 3% anual. La presión cambiaria usa la inflación, el déficit y el tipo de cambio real del año anterior. El canal comercial también actúa con un año de rezago.
- Flotación pura: la depreciación iguala la presión; intervención cero. Paridad fija: depreciación cero mientras la intervención necesaria es financiable. Una unidad de presión requiere 0,30 puntos del índice de reservas. Es una escala ilustrativa, no % del PIB ni una elasticidad estimada.
- Si las reservas no alcanzan, se venden las restantes y la presión residual ajusta la cotización. Desde entonces se mantiene flotación; no se restablece automáticamente la paridad. El fin del año de transición puede tener intervención y depreciación simultáneas.
- Para aislar el canal cambiario, se supone compensado el efecto de las compras/ventas de divisas sobre la liquidez. No hay un balance monetario completo; tasa y emisión son controles independientes. Esto no representa un régimen con perfecta movilidad de capitales ni una caja de conversión.
- El traslado cambiario a precios es parcial y se mide respecto de la depreciación de referencia (21,36% anual, compatible con 25% de inflación local y 3% externa). Por eso un tipo de cambio fijo reduce la presión inflacionaria, sin eliminarla automáticamente.
- El crecimiento tendencial es 2%; el impulso de políticas se atenúa 28% anual. El desempleo responde al crecimiento y tiene piso 2% y techo 30%.
- El déficit es global: incluye costos financieros estilizados. La deuda heredada se indexa por inflación, lo que se cancela con los precios del denominador; el crecimiento real reduce esa relación. Todo déficit se financia con deuda; la emisión no se descuenta de ese financiamiento. No hay deuda en divisas ni efectos de valuación cambiaria. Deuda y reservas tienen piso cero.
- No se modelan todavía exportaciones/importaciones por separado, balanza de pagos completa, capitales, tasa internacional, expectativas prospectivas, restricciones de crédito ni riesgo país. El canal comercial es una aproximación vía tipo de cambio real; los resultados no son pronósticos.
- **Beta 0.3:** reemplaza la regla anterior de reservas por intervención cambiaria y agrega el canal real y el traslado a precios. Sus resultados difieren de beta 0.2 y de guías anteriores.
""")
    st.code("""impulso = 0.85·Δgasto - 0.55·Δimpuestos - 0.22·Δtasa + 0.12·Δemisión
brecha(t) = impulso·0.72^(t-1)
crecimiento(t) = 2 + 0.55·brecha(t) - 0.05·máx(inflación(t-1)-25, 0) + 0.015·[TCR(t-1)-100]
presión(t) = 100·[(1+inflación(t-1)/100)/1.03-1] + 0.8·Δemisión + 0.6·brecha(t) + 0.30·[déficit(t-1)-3] - 0.5·Δtasa - 0.06·[TCR(t-1)-100]
Flexible: intervención(t) = 0; depreciación(t) = presión(t)
Fijo: intervención(t) = máx(-reservas(t-1), -0.30·presión(t))
      depreciación(t) = presión(t) + intervención(t)/0.30
reservas(t) = reservas(t-1) + intervención(t)
TCN(t) = TCN(t-1)·[1+depreciación(t)/100]
inflación(t) = máx(0, 0.70·inflación(t-1) + 0.30·[25 + 0.65·Δemisión + 0.55·brecha(t) - 0.45·Δtasa + 0.20·máx(-Δimpuestos, 0) + 0.25·(depreciación(t)-21.3592233)])
TCR(t) = TCR(t-1)·[1+depreciación(t)/100]·1.03/[1+inflación(t)/100]
PIB(t) = PIB(t-1)·[1+crecimiento(t)/100]
desempleo(t) = desempleo(t-1) - 0.30·[crecimiento(t)-2] (entre 2% y 30%)
déficit(t) = 3 + Δgasto - Δimpuestos - 0.20·[crecimiento(t)-2] + 0.025·[deuda(t-1)-60]
deuda(t) = máx(0, deuda(t-1)/[1+crecimiento(t)/100] + déficit(t))""", language="text")

with st.expander("Tabla de resultados"):
    st.dataframe(escenario.rename(columns={**etiquetas, "depreciacion": "Depreciación anual (%)", "intervencion": "Intervención (puntos del índice de reservas)", "presion_cambiaria": "Presión cambiaria (pp)", "abandono_fijo": "Paridad abandonada"}).round(2))
st.download_button("Descargar escenario CSV", escenario.round(3).to_csv().encode("utf-8-sig"),
                   "escenario_macroeconomico.csv", "text/csv")
