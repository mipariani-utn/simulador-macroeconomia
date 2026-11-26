"""Modelo macroeconómico didáctico; índices y parámetros ilustrativos."""
from dataclasses import dataclass
from math import isfinite

VERSION_MODELO = "0.3"
INFLACION_EXTERNA = 3.0
DEPRECIACION_REFERENCIA = 100 * (1.25 / 1.03 - 1)
SENSIBILIDAD_DIVISAS = 0.30


@dataclass(frozen=True)
class Politica:
    gasto: float = 0.0       # cambio sostenido del gasto, puntos del PIB
    impuestos: float = 0.0   # cambio de presión tributaria, puntos del PIB
    tasa: float = 0.0        # cambio de tasa nominal, puntos porcentuales
    emision: float = 0.0     # crecimiento adicional de dinero, puntos porcentuales
    regimen: str = "Flexible"  # flotación pura o paridad fija inicial


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
    if isinstance(periodos, bool) or not isinstance(periodos, int):
        raise ValueError("periodos debe ser un número entero")
    if p.regimen not in ("Fijo", "Flexible"):
        raise ValueError("El régimen debe ser Fijo o Flexible")
    if not all(isfinite(v) for v in (p.gasto, p.impuestos, p.tasa, p.emision)):
        raise ValueError("Los controles deben ser números finitos")
    if not 1 <= periodos <= 30:
        raise ValueError("periodos debe estar entre 1 y 30")
    if not (-5 <= p.gasto <= 5 and -5 <= p.impuestos <= 5
            and -10 <= p.tasa <= 10 and -15 <= p.emision <= 15):
        raise ValueError("Política fuera de los rangos didácticos")

    y, inflacion, desempleo, reservas = 100.0, 25.0, 8.0, 100.0
    deuda = 60.0
    tc_nominal = tc_real = 100.0
    precios = precios_externos = 100.0
    abandono_fijo = False
    serie = [dict(anio=0, pib=y, inflacion=inflacion, desempleo=desempleo,
                  deficit=3.0, reservas=reservas, deuda=deuda, crecimiento=None,
                  tc_nominal=tc_nominal, tc_real=tc_real, depreciacion=None,
                  intervencion=0.0, presion_cambiaria=None, abandono_fijo=False)]
    for anio in range(1, periodos + 1):
        # La brecha de producto combina impulso fiscal, costo del crédito y
        # estímulo monetario; se atenúa con el tiempo (capacidad y expectativas).
        impulso = 0.85 * p.gasto - 0.55 * p.impuestos - 0.22 * p.tasa + 0.12 * p.emision
        brecha = impulso * (0.72 ** (anio - 1))
        # El canal comercial usa el tipo de cambio real del año previo.
        # Coeficientes ilustrativos: no son elasticidades estimadas.
        crecimiento = (2.0 + 0.55 * brecha - 0.05 * max(inflacion - 25.0, 0)
                       + 0.015 * (tc_real - 100))
        # Presión de divisas anterior a la intervención. El déficit heredado
        # evita una dependencia circular con crecimiento/deuda del mismo año.
        diferencial = 100 * ((1 + inflacion / 100) / (1 + INFLACION_EXTERNA / 100) - 1)
        presion = (diferencial + 0.8 * p.emision + 0.6 * brecha
                   + 0.30 * (serie[-1]["deficit"] - 3) - 0.5 * p.tasa
                   - 0.06 * (tc_real - 100))
        intervencion = 0.0  # positivo: compra de divisas; negativo: venta
        depreciacion = presion
        if p.regimen == "Fijo" and not abandono_fijo:
            intervencion_necesaria = -SENSIBILIDAD_DIVISAS * presion
            intervencion = max(-reservas, intervencion_necesaria)
            reservas = max(0.0, reservas + intervencion)
            # La intervención cubre la presión hasta donde alcanzan reservas.
            depreciacion = presion + intervencion / SENSIBILIDAD_DIVISAS
            if reservas <= 1e-10 and intervencion_necesaria < 0:
                reservas = 0.0
                abandono_fijo = True
        tc_nominal *= 1 + depreciacion / 100
        y *= 1 + crecimiento / 100
        desempleo = max(2.0, min(30.0, desempleo - 0.30 * (crecimiento - 2.0)))
        objetivo_inflacion = (25.0 + 0.65 * p.emision + 0.55 * brecha
                              - 0.45 * p.tasa + 0.20 * max(0, -p.impuestos)
                              + 0.25 * (depreciacion - DEPRECIACION_REFERENCIA))
        inflacion = max(0.0, 0.70 * inflacion + 0.30 * objetivo_inflacion)
        # Déficit y deuda como % del PIB; recaudación automática con la actividad.
        deficit = 3.0 + p.gasto - p.impuestos - 0.20 * (crecimiento - 2.0) + 0.025 * (deuda - 60)
        deuda = actualizar_deuda(deuda, deficit, crecimiento)
        precios *= 1 + inflacion / 100
        precios_externos *= 1 + INFLACION_EXTERNA / 100
        tc_real = tc_nominal * precios_externos / precios
        serie.append(dict(anio=anio, pib=y, inflacion=inflacion,
                          desempleo=desempleo, deficit=deficit,
                          reservas=reservas, deuda=deuda, crecimiento=crecimiento,
                          tc_nominal=tc_nominal, tc_real=tc_real,
                          depreciacion=depreciacion, intervencion=intervencion,
                          presion_cambiaria=presion, abandono_fijo=abandono_fijo))
    return serie
