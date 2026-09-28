# Simulador macroeconómico didáctico

Interfaz interactiva para explorar cambios sostenidos de gasto público, impuestos, tasa de interés y emisión durante 2 a 15 años. Grafica PIB real, inflación, desempleo, déficit fiscal y reservas frente a una trayectoria sin cambios.

## Ejecutar

Requiere Python 3.10 o superior. En la carpeta de estos tres archivos:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Se abre una página local en el navegador. Mové los controles del panel lateral; los gráficos se actualizan automáticamente. Podés descargar el escenario como CSV.

## Alcance

Todos los valores iniciales y coeficientes son **ilustrativos**, no una calibración con datos de Argentina. El PIB y las reservas son índices con base 100. Inflación y desempleo se expresan en porcentajes; gasto y déficit, en proporción del PIB; impuestos, tasa y emisión, en cambios de puntos porcentuales según se indique. El modelo incorpora relaciones simplificadas de demanda agregada, inflación inercial, desempleo, balance fiscal y reservas. La pestaña de supuestos de la interfaz muestra las ecuaciones y límites. No debe usarse para predicción ni para decisiones de política pública.
