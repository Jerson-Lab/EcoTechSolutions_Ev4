import json

from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from errores_api import mensaje_error_http

from validaciones import validar_ciudad

def obtener_json(url):
    with  urlopen(url, timeout=10) as respuesta:
        if respuesta.status != 200:
            raise ValueError("Respuesta HTTP inesperada")
        
        contenido = respuesta.read().decode("utf-8")

    datos = json.loads(contenido)
    if not isinstance(datos, dict):
        raise ValueError("Formato JSON incorrecto")
    
    return datos

def buscar_ciudad(ciudad):
    parametros = {
        "name": ciudad,
        "count": 1,
        "language": "es",
        "countryCode": "CL",
        "format": "json"
    }

    url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urlencode(parametros)
    )

    datos = obtener_json(url)

    resultados = datos.get("results", [])

    if not resultados:
        return None

    return resultados [0]

def describir_estado_tiempo(codigo):
    estados = {
        0: "Despejado",
        1: "Mayormente despejado",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla",
        48: "Niebla",
        51: "Llovizna ligera",
        53: "Llovizna moderada",
        55: "Llovizna intensa",
        61: "lluvia ligera",
        63: "lluvia moderada",
        65: "lluvia intensa",
        80: "Chubascos ligeros",
        81: "Chubascos moderados",
        82: "Chubascos intensos",
        95: "Tormenta",
        96: "Tormenta con granizo",
        99: "Tormenta con granizo",
    }

    return estados.get(codigo, "Estado no disponible")

def consultar_clima():
    print("\n=== CONSULTA DEL CLIMA ===")

    ciudad = input ("Ingrese una ciudad de Chile: ").strip()

    if not validar_ciudad(ciudad):
        print("Nombre de ciudad Invalido.")
        return

    try:
        ubicacion = buscar_ciudad(ciudad)

        if ubicacion is None:
            print("No se econtró la ciudad.")
            return

        parametros = {
            "latitude": ubicacion["latitude"],
            "longitude": ubicacion["longitude"],
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "timezone": ubicacion.get(
                "timezone", "America/Santiago"
            )
        }

        url = (
            "https://api.open-meteo.com/v1/forecast?"
            + urlencode(parametros)
        )

        datos = obtener_json(url)

        clima = datos["current"]

        if not isinstance(clima, dict):
            raise ValueError("Estructura climatica inválida")
        codigo_clima = clima.get("weather_code")
        estado = describir_estado_tiempo(codigo_clima)

        print("\n=== RESULTADO DEL CLIMA ===")
        print(f"Ciudad: {ubicacion['name']}")
        print(f"Región: {ubicacion.get('admin1', 'Chile')}")
        print(f"Fecha y hora: {clima['time']}")

        print(f"Temperatura: {clima['temperature_2m']} °C")
        print(f"Humedad: {clima['relative_humidity_2m']} %")
        print(f"Viento: {clima['wind_speed_10m']} km/h")
        print(f"Estado del tiempo: {estado}")

    except HTTPError as error:
        print(mensaje_error_http(error.code))
    except (
        URLError,
        TimeoutError,
        OSError
    ):
        print("Error de conexión con el servicio del clima.")
        print("Intente nuevamente más tarde.")
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        KeyError,
        TypeError,
        ValueError
    ):
        print("El servicio del clima devolvió datos inválidos.")
        print("No fue posible completar la consulta.")