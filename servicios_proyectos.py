
import math

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlencode

from clima import (
    buscar_ciudad,
    obtener_json,
    describir_estado_tiempo
)

from monedas import obtener_cotizaciones


def consultar_clima_proyecto(proyecto):
    if proyecto is None or not proyecto.activo:
        raise ValueError("Proyecto no disponible.")

    ubicacion = buscar_ciudad(proyecto.ciudad)

    if not isinstance(ubicacion, dict):
        raise ValueError("No se encontró la ciudad.")

    try:
        latitud = float(ubicacion["latitude"])
        longitud = float(ubicacion["longitude"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Coordenadas inválidas.") from error

    if not (
        math.isfinite(latitud)
        and math.isfinite(longitud)
        and -90 <= latitud <= 90
        and -180 <= longitud <= 180
    ):
        raise ValueError("Coordenadas fuera de rango.")

    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "timezone": "auto"
    }

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urlencode(parametros)
    )


    datos = obtener_json(url)

    if not isinstance(datos, dict):
        raise ValueError(
            "Respuesta meteorológica inválida."
        )

    actual = datos.get("current")

    if not isinstance(actual, dict):
        raise ValueError("Datos climáticos incompletos.")

    try:
        temperatura = float(actual["temperature_2m"])
        humedad = float(actual["relative_humidity_2m"])
        viento = float(actual["wind_speed_10m"])
        codigo = int(actual["weather_code"])
        fecha = str(actual["time"])

    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Respuesta climática inválida.") from error

    if not all(
        math.isfinite(x)
        for x in (temperatura, humedad, viento)
    ):
        raise ValueError("Valores meteorológicos inválidos.")

    return {
        "proyecto": proyecto.nombre,
        "ciudad": proyecto.ciudad,
        "temperatura": temperatura,
        "humedad": humedad,
        "viento": viento,
        "estado": describir_estado_tiempo(codigo),
        "fecha": fecha
    }


def convertir_presupuesto_proyecto(proyecto):
    if proyecto is None or not proyecto.activo:
        raise ValueError("Proyecto no disponible.")

    monto = (
        Decimal(proyecto.presupuesto_centavos)
        / Decimal("100")
    )

    moneda = proyecto.moneda.upper()

    if moneda == "CLP":
        tasa = Decimal("1")
        fecha = "No requiere conversión"

    elif moneda in ("USD", "EUR"):
        datos = obtener_cotizaciones(moneda)

        if (
            not isinstance(datos, dict)
            or datos.get("result") != "success"
            or datos.get("base_code") != moneda
            or not isinstance(datos.get("rates"), dict)
        ):
            raise ValueError(
                "Respuesta de cotizaciones inválida."
            )

        try:
            tasa = Decimal(str(datos["rates"]["CLP"]))
        except (
            KeyError, TypeError, ValueError, InvalidOperation
        ) as error:
            raise ValueError(
                "Tasa de conversión inválida."
            ) from error

        if not tasa.is_finite() or tasa <= 0:
            raise ValueError(
                "La tasa debe ser positiva y válida."
            )

        fecha = datos.get(
            "time_last_update_utc",
            "No disponible"
        )

    else:
        raise ValueError("Moneda no permitida.")

    equivalente = (monto * tasa).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP
    )

    return {
        "proyecto": proyecto.nombre,
        "monto": monto,
        "moneda": moneda,
        "tasa": tasa,
        "equivalente_clp": equivalente,
        "fecha": fecha
    }
