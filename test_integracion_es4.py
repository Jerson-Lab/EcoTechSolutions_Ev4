
import unittest

from decimal import Decimal
from urllib.error import URLError
from unittest.mock import patch

from proyectos import Proyecto
from servicios_proyectos import (
    consultar_clima_proyecto,
    convertir_presupuesto_proyecto
)


class TestIntegracionES4(unittest.TestCase):

    def setUp(self):
        self.proyecto = Proyecto(
            nombre="Proyecto Solar",
            descripcion="Instalación solar",
            ciudad="Chillán",
            fecha_inicio="2026-12-01",
            fecha_fin="2027-01-31",
            presupuesto_centavos=125000,
            moneda="USD"
        )

    def datos_clima(self):
        return {
            "current": {
                "temperature_2m": 21.5,
                "relative_humidity_2m": 60,
                "wind_speed_10m": 10.0,
                "weather_code": 1,
                "time": "2026-12-01T12:00"
            }
        }

    def datos_monedas(self, moneda, tasa):
        return {
            "result": "success",
            "base_code": moneda,
            "rates": {"CLP": tasa}
        }

    # PRUEBAS DE CLIMA

    @patch("servicios_proyectos.obtener_json")
    @patch("servicios_proyectos.buscar_ciudad")
    def test_01_clima_correcto(self, ciudad, api):
        ciudad.return_value = {
            "latitude": -36.6,
            "longitude": -72.1
        }

        api.return_value = self.datos_clima()

        resultado = consultar_clima_proyecto(
            self.proyecto
        )

        self.assertEqual(resultado["ciudad"], "Chillán")
        self.assertEqual(resultado["temperatura"], 21.5)
        self.assertEqual(
            resultado["estado"], "Mayormente despejado"
        )

    @patch("servicios_proyectos.buscar_ciudad")
    def test_02_ciudad_inexistente(self, ciudad):
        ciudad.return_value = None

        with self.assertRaises(ValueError):
            consultar_clima_proyecto(self.proyecto)

    @patch("servicios_proyectos.obtener_json")
    @patch("servicios_proyectos.buscar_ciudad")
    def test_03_clima_incompleto(self, ciudad, api):
        ciudad.return_value = {
            "latitude": -36.6,
            "longitude": -72.1
        }

        api.return_value = {"current": {}}

        with self.assertRaises(ValueError):
            consultar_clima_proyecto(self.proyecto)

    @patch("servicios_proyectos.obtener_json")
    @patch("servicios_proyectos.buscar_ciudad")
    def test_04_respuesta_invalida(self, ciudad, api):
        ciudad.return_value = {
            "latitude": -36.6,
            "longitude": -72.1
        }

        api.return_value = None

        with self.assertRaises(ValueError):
            consultar_clima_proyecto(self.proyecto)

    @patch("servicios_proyectos.obtener_json")
    @patch("servicios_proyectos.buscar_ciudad")
    def test_05_error_conexion(self, ciudad, api):
        ciudad.return_value = {
            "latitude": -36.6,
            "longitude": -72.1
        }

        api.side_effect = URLError(
            "Servicio no disponible"
        )

        with self.assertRaises(URLError):
            consultar_clima_proyecto(self.proyecto)

    # PRUEBAS DE MONEDAS

    @patch("servicios_proyectos.obtener_cotizaciones")
    def test_06_conversion_usd(self, api):
        api.return_value = self.datos_monedas(
            "USD", 1000
        )

        resultado = convertir_presupuesto_proyecto(
            self.proyecto
        )

        self.assertEqual(
            resultado["equivalente_clp"],
            Decimal("1250000")
        )

    @patch("servicios_proyectos.obtener_cotizaciones")
    def test_07_conversion_eur(self, api):
        self.proyecto.moneda = "EUR"

        api.return_value = self.datos_monedas(
            "EUR", 1100
        )

        resultado = convertir_presupuesto_proyecto(
            self.proyecto
        )

        self.assertEqual(
            resultado["equivalente_clp"],
            Decimal("1375000")
        )

    @patch("servicios_proyectos.obtener_cotizaciones")
    def test_08_presupuesto_clp(self, api):
        self.proyecto.moneda = "CLP"

        resultado = convertir_presupuesto_proyecto(
            self.proyecto
        )

        self.assertEqual(
            resultado["equivalente_clp"],
            Decimal("1250")
        )

        api.assert_not_called()

    @patch("servicios_proyectos.obtener_cotizaciones")
    def test_09_moneda_base_incorrecta(self, api):
        api.return_value = self.datos_monedas(
            "EUR", 1000
        )

        with self.assertRaises(ValueError):
            convertir_presupuesto_proyecto(
                self.proyecto
            )

    @patch("servicios_proyectos.obtener_cotizaciones")
    def test_10_tasa_invalida(self, api):
        api.return_value = self.datos_monedas(
            "USD", -1
        )

        with self.assertRaises(ValueError):
            convertir_presupuesto_proyecto(
                self.proyecto
            )

    # VALIDACIÓN DE ACCESO A PROYECTOS

    @patch("servicios_proyectos.obtener_cotizaciones")
    @patch("servicios_proyectos.buscar_ciudad")
    def test_11_proyecto_inactivo(self, ciudad, api):
        self.proyecto.activo = False

        with self.assertRaises(ValueError):
            consultar_clima_proyecto(self.proyecto)

        with self.assertRaises(ValueError):
            convertir_presupuesto_proyecto(
                self.proyecto
            )

        ciudad.assert_not_called()
        api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
