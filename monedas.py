import json
import re
from errores_api import mensaje_error_http

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

MONEDAS_PERMITIDAS = {
    "1": "USD",
    "2": "EUR"
}

URL_BASE = "https://open.er-api.com/v6/latest/"

def obtener_cotizaciones(moneda):
    if moneda not in ("USD", "EUR"):
        raise ValueError("Moneda no permitida.")

    url = URL_BASE + moneda

    with urlopen(url, timeout=10) as respuesta:
        if respuesta.status != 200:
            raise ValueError("Respuesta HTTP inesperada")

        datos = json.load(respuesta)

    return datos

def consultar_tipo_cambio():
    print("\n=== CONSULTA DE TIPO DE CAMBIO ===")
    print("1. Dólar estadounidense (USD)")
    print("2. Euro (EUR)")

    opcion = input("Seleccione una moneda: ").strip()

    if opcion not in MONEDAS_PERMITIDAS:
        print("Moneda no válida.")
        return

    moneda = MONEDAS_PERMITIDAS[opcion]

    texto_monto = input(f"Ingrese el monto en {moneda}: ").strip().replace(",",".")

    patron = r"\d{1,9}(\.\d{1,2})?"

    if not re.fullmatch(patron, texto_monto):
        print("Monto inválido. Use un número positivo.")
        return

    monto = Decimal(texto_monto)

    if monto <= 0: 
        print("El monto debe ser mayor que cero.")
        return

    try:
        datos = obtener_cotizaciones(moneda)

        if(
            not isinstance(datos, dict)
            or datos.get("result") != "success"
            or datos.get("base_code") != moneda
        ):
            raise ValueError("Respuesta inválida de la API")

        tasas = datos.get("rates")

        if not isinstance(tasas, dict):
            raise ValueError("Tasas no disponibles")

        tasa = Decimal(str(tasas["CLP"]))

        if not tasa.is_finite() or tasa <= 0:
            raise ValueError("Tipo de cambio inválido")

        equivalente = (monto * tasa).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )

        print("\n=== RESULTADO DE CONVERSIÓN ===")
        print(f"Moneda: {moneda}")
        print(f"Monto original: {monto} {moneda}")
        print(f"1 {moneda} = {tasa} CLP")
        print(f"Equivalente estimado: {equivalente} CLP")

        fecha = datos.get(
            "time_last_update_utc",
            "No disponible"
        )

        print(f"Última actualizacion (UTC): {fecha}")
        print("Valor referencial, no bancario.")
        print("Fuente: Rates By Exchange Rate API")
        print("https://www.exchangerate-api.com")

    except HTTPError as error:
        print(mensaje_error_http(error.code))

    except (
        URLError, 
        TimeoutError, 
        OSError):
        print("Error de conexión con el servicio de monedas.")
        print("Intente nuevamente más tarde.")

    except(
        ValueError, 
        KeyError, 
        TypeError, 
        InvalidOperation):
        print("La API devolvió datos inválidos o incompletos.")

    