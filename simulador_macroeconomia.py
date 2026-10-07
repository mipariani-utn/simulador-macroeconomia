"""Modelo macroeconómico didáctico; índices y parámetros ilustrativos."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Politica:
    gasto: float = 0.0       # cambio sostenido del gasto, puntos del PIB
    impuestos: float = 0.0   # cambio de presión tributaria, puntos del PIB
    tasa: float = 0.0        # cambio de tasa nominal, puntos porcentuales
    emision: float = 0.0     # crecimiento adicional de dinero, puntos porcentuales


def actualizar_deuda(deuda_anterior: float, deficit: float, crecimiento: float) -> float:
    """Deuda/PIB con principal indexado y déficit global financiado con deuda.

    El déficit es % del PIB corriente. La inflación ajusta tanto el principal
    como el denominador; por eso se cancelan en esta simplificación. No se
    agregan intereses nuevamente: el déficit ya incluye costos financieros.
    """
    if crecimiento <= -100:
        raise ValueError("El crecimiento debe ser mayor que -100%")
    return max(0.0, deuda_anterior / (1 + crecimiento / 100) + deficit)


def simular(p: Politica, periodos: int = 8) -> list[dict[str, float | None]]:
    """Trayectoria anual estilizada. La política se sostiene desde el año 1."""
    if not 1 <= periodos <= 30:
        raise ValueError("periodos debe estar entre 1 y 30")
    if not (-5 <= p.gasto <= 5 and -5 <= p.impuestos <= 5
            and -10 <= p.tasa <= 10 and -15 <= p.emision <= 15):
        raise ValueError("Política fuera de los rangos didácticos")

    y, inflacion, desempleo, reservas = 100.0, 25.0, 8.0, 100.0
    deuda = 60.0
    serie = [dict(anio=0, pib=y, inflacion=inflacion, desempleo=desempleo,
                  deficit=3.0, reservas=reservas, deuda=deuda, crecimiento=None)]
    for anio in range(1, periodos + 1):
        # La brecha de producto combina impulso fiscal, costo del crédito y
        # estímulo monetario; se atenúa con el tiempo (capacidad y expectativas).
        impulso = 0.85 * p.gasto - 0.55 * p.impuestos - 0.22 * p.tasa + 0.12 * p.emision
        brecha = impulso * (0.72 ** (anio - 1))
        crecimiento = 2.0 + 0.55 * brecha - 0.05 * max(inflacion - 25.0, 0)
        y *= 1 + crecimiento / 100
        desempleo = max(2.0, min(30.0, desempleo - 0.30 * (crecimiento - 2.0)))
        objetivo_inflacion = (25.0 + 0.65 * p.emision + 0.55 * brecha
                              - 0.45 * p.tasa + 0.20 * max(0, -p.impuestos))
        inflacion = max(0.0, 0.70 * inflacion + 0.30 * objetivo_inflacion)
        # Déficit y deuda como % del PIB; recaudación automática con la actividad.
        deficit = 3.0 + p.gasto - p.impuestos - 0.20 * (crecimiento - 2.0) + 0.025 * (deuda - 60)
        deuda = actualizar_deuda(deuda, deficit, crecimiento)
        # Reservas son un índice (año 0 = 100), no miles de millones de USD.
        reservas = max(0.0, reservas + 1.0 + 0.5 * p.tasa - 0.8 * p.emision
                       - 0.6 * max(brecha, 0) - 0.30 * max(deficit - 3, 0))
        serie.append(dict(anio=anio, pib=y, inflacion=inflacion,
                          desempleo=desempleo, deficit=deficit,
                          reservas=reservas, deuda=deuda, crecimiento=crecimiento))
    return serie
