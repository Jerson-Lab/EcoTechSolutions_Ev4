
import hashlib
import io
import json
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from urllib.error import HTTPError

import clima
import main
import seguridad
import monedas

from validaciones import (
    validar_usuario,
    validar_contrasena,
    validar_ciudad
)


class PruebasEcoTech(unittest.TestCase):

    def test_usuario_valido(self):
        self.assertTrue(validar_usuario("alumno01"))

    def test_usuario_invalido(self):
        self.assertFalse(validar_usuario("ab"))

    def test_contrasena_valida(self):
        self.assertTrue(
            validar_contrasena("ClaveSegura2026")
        )

    def test_contrasena_invalida(self):
        self.assertFalse(
            validar_contrasena("soloLetras")
        )

    def test_ciudad_valida(self):
        self.assertTrue(validar_ciudad("Viña del Mar"))

    def test_ciudad_invalida(self):
        self.assertFalse(validar_ciudad("Ciudad123"))

    def test_registro_protege_contrasena(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "usuarios.json"

            with patch.object(seguridad, "RUTA_USUARIOS", ruta), \
                 patch("builtins.input", return_value="alumno01"), \
                 patch(
                     "seguridad.getpass.getpass",
                     side_effect=["ClaveSegura2026", "ClaveSegura2026"]
                 ), \
                 redirect_stdout(io.StringIO()):
                seguridad.registrar_usuario()

            contenido = ruta.read_text(encoding="utf-8")
            datos = json.loads(contenido)

            self.assertIn("alumno01", datos)
            self.assertIn("hash", datos["alumno01"])
            self.assertIn("salt", datos["alumno01"])
            self.assertNotIn("ClaveSegura2026", contenido)

    def test_inicio_sesion_correcto(self):
        contrasena = "ClaveSegura2026"
        salt = b"1234567890abcdef"

        hash_guardado = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            salt,
            seguridad.ITERACIONES
        )

        usuarios = {
            "alumno01": {
                "salt": salt.hex(),
                "hash": hash_guardado.hex(),
                "iteraciones": seguridad.ITERACIONES
            }
        }

        with patch("seguridad.cargar_usuarios", return_value=usuarios), \
             patch("builtins.input", return_value="alumno01"), \
             patch("seguridad.getpass.getpass", return_value=contrasena), \
             redirect_stdout(io.StringIO()):
            resultado = seguridad.iniciar_sesion()

        self.assertEqual(resultado, "alumno01")

    def test_no_abrir_menu_sin_login(self):
        with patch("builtins.input", side_effect=["2", "3"]), \
             patch("main.iniciar_sesion", return_value=None), \
             patch("main.menu_privado") as menu, \
             redirect_stdout(io.StringIO()):
            main.main()

        menu.assert_not_called()

    def test_clima_sin_internet(self):
        ubicacion = {
            "name": "Chillán",
            "admin1": "Ñuble",
            "latitude": -36.6,
            "longitude": -72.1,
            "timezone": "America/Santiago"
        }

        respuesta = {
            "current": {
                "time": "2026-11-12T15:00",
                "temperature_2m": 20,
                "relative_humidity_2m": 50,
                "wind_speed_10m": 10,
                "weather_code": 3
            }
        }

        salida = io.StringIO()

        with patch("builtins.input", return_value="Chillán"), \
             patch("clima.buscar_ciudad", return_value=ubicacion), \
             patch("clima.obtener_json", return_value=respuesta), \
             redirect_stdout(salida):
            clima.consultar_clima()

        self.assertIn(
            "Temperatura: 20 °C",
            salida.getvalue()
        )

        self.assertIn(
            "Humedad: 50 %",
            salida.getvalue()
        )

        self.assertIn(
            "Estado del tiempo: Nublado",
            salida.getvalue()
        )

    def test_ciudad_invalida_no_consulta_api(self):
        with patch("builtins.input", return_value="Ciudad123"), \
             patch("clima.buscar_ciudad") as buscar, \
             redirect_stdout(io.StringIO()):
            clima.consultar_clima()

        buscar.assert_not_called()

    def test_http_200_clima(self):
        respuesta = MagicMock()

        respuesta.status = 200
        respuesta.read.return_value = b'{"temperatura": 20}'
        respuesta.__enter__.return_value = respuesta

        with patch("clima.urlopen", return_value=respuesta):
            datos = clima.obtener_json("https://ejemplo.test")

        self.assertEqual(datos["temperatura"], 20)

    def test_http_404_clima(self):
        error = HTTPError(
            "https://ejemplo.test",
            404,
            "Not Found",
            None,
            None
        )

        salida = io.StringIO()

        with patch("builtins.input", return_value="Chillán"), \
             patch("clima.buscar_ciudad", side_effect=error), \
             redirect_stdout(salida):

            clima.consultar_clima()

        self.assertIn("HTTP 404", salida.getvalue())

    def test_http_429_monedas(self):
        error = HTTPError(
            "https://ejemplo.test",
            429,
            "Too Many Requests",
            None,
            None
        )

        salida = io.StringIO()

        with patch("builtins.input", side_effect=["1", "100"]), \
             patch(
                 "monedas.obtener_cotizaciones",
                 side_effect=error
             ), \
             redirect_stdout(salida):

            monedas.consultar_tipo_cambio()

        self.assertIn("HTTP 429", salida.getvalue())


    def test_http_500_monedas(self):
        error = HTTPError(
            "https://ejemplo.test",
            500,
            "Internal Server Error",
            None,
            None
        )

        salida = io.StringIO()

        with patch("builtins.input", side_effect=["1", "100"]), \
             patch(
                 "monedas.obtener_cotizaciones",
                 side_effect=error
             ), \
             redirect_stdout(salida):

            monedas.consultar_tipo_cambio()

        self.assertIn("HTTP 500", salida.getvalue())


    def test_conversion_usd(self):
        respuesta = {
            "result": "success",
            "base_code": "USD",
            "rates": {"CLP": 900},
            "time_last_update_utc": "Fecha de prueba"
        }

        salida = io.StringIO()

        with patch("builtins.input", side_effect=["1", "100"]), \
             patch(
                 "monedas.obtener_cotizaciones",
                 return_value=respuesta
             ), \
             redirect_stdout(salida):

            monedas.consultar_tipo_cambio()

        self.assertIn(
            "Equivalente estimado: 90000 CLP",
            salida.getvalue()
        )

    def test_moneda_invalida(self):
        with patch("builtins.input", return_value="9"), \
             patch("monedas.obtener_cotizaciones") as consulta, \
             redirect_stdout(io.StringIO()):

            monedas.consultar_tipo_cambio()

        consulta.assert_not_called()

    def test_monto_invalido(self):
        with patch("builtins.input", side_effect=["1", "-100"]), \
             patch("monedas.obtener_cotizaciones") as consulta, \
             redirect_stdout(io.StringIO()):

            monedas.consultar_tipo_cambio()

        consulta.assert_not_called()

    def test_archivo_usuarios_formato_invalido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "usuarios.json"
            ruta.write_text("[]", encoding="utf-8")

            with patch.object(seguridad, "RUTA_USUARIOS", ruta), \
                 redirect_stdout(io.StringIO()):
                resultado = seguridad.cargar_usuarios()

            self.assertIsNone(resultado)

    def test_respuesta_clima_malformada(self):
        ubicacion = {
            "name": "Chillán",
            "latitude": -36.6,
            "longitude": -72.1
        }

        salida = io.StringIO()

        with patch("builtins.input", return_value="Chillán"), \
             patch("clima.buscar_ciudad", return_value=ubicacion), \
             patch(
                 "clima.obtener_json",
                 return_value={"current": None}
             ), \
             redirect_stdout(salida):
            clima.consultar_clima()

        self.assertIn("datos inválidos", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
