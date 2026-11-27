
import sqlite3
import unittest
import base_datos

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from contextlib import closing

from empleados import Empleado, RepositorioEmpleados
from proyectos import Proyecto, RepositorioProyectos
from asignaciones import RepositorioAsignaciones


class TestModulosES4(unittest.TestCase):

    def setUp(self):
        # Cada prueba utiliza su propia base de datos.
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)

        ruta = Path(self.temporal.name) / "pruebas.db"

        parche = patch.object(base_datos, "RUTA_BD", ruta)
        parche.start()
        self.addCleanup(parche.stop)

        base_datos.inicializar_base_datos()

        self.empleados = RepositorioEmpleados()
        self.proyectos = RepositorioProyectos()
        self.asignaciones = RepositorioAsignaciones()

    def crear_empleado(self):
        return self.empleados.registrar(
            Empleado(
                nombre="Ana Rojas",
                cargo="Analista",
                correo="ana@ejemplo.cl"
            )
        )

    def crear_proyecto(self, nombre="Proyecto Solar"):
        return self.proyectos.registrar(
            Proyecto(
                nombre=nombre,
                descripcion="Instalación de paneles",
                ciudad="Chillán",
                fecha_inicio="2026-12-01",
                fecha_fin="2027-01-31",
                presupuesto_centavos=150000000,
                moneda="CLP"
            )
        )

    # =========================================
    # PRUEBAS DE EMPLEADOS
    # =========================================

    def test_01_registrar_empleado(self):
        empleado_id = self.crear_empleado()

        empleado = self.empleados.buscar_por_id(
            empleado_id
        )

        self.assertIsNotNone(empleado)
        self.assertEqual(empleado.nombre, "Ana Rojas")

    def test_02_modificar_empleado(self):
        empleado_id = self.crear_empleado()

        modificado = Empleado(
            nombre="Ana Pérez",
            cargo="Jefa de Proyectos",
            correo="ana@ejemplo.cl"
        )

        resultado = self.empleados.modificar(
            empleado_id, modificado
        )

        # Consultamos nuevamente desde SQLite.
        actualizado = self.empleados.buscar_por_id(
            empleado_id
        )

        self.assertTrue(resultado)
        self.assertEqual(
            actualizado.nombre, "Ana Pérez"
        )
        self.assertEqual(
            actualizado.cargo, "Jefa de Proyectos"
        )

    def test_03_correo_duplicado(self):
        self.crear_empleado()

        with self.assertRaises(sqlite3.IntegrityError):
            self.empleados.registrar(
                Empleado(
                    nombre="Pedro Soto",
                    cargo="Técnico",
                    correo="ana@ejemplo.cl"
                )
            )

    def test_04_empleado_invalido(self):
        with self.assertRaises(ValueError):
            self.empleados.registrar(
                Empleado(
                    nombre="A",
                    cargo="Analista",
                    correo="correo@ejemplo.cl"
                )
            )

    def test_05_desactivar_reactivar_empleado(self):
        empleado_id = self.crear_empleado()

        self.assertTrue(
            self.empleados.desactivar(empleado_id)
        )
        self.assertIsNone(
            self.empleados.buscar_por_id(empleado_id)
        )

        inactivos = self.empleados.listar_inactivos()

        self.assertEqual(len(inactivos), 1)

        self.assertTrue(
            self.empleados.reactivar(empleado_id)
        )
        self.assertIsNotNone(
            self.empleados.buscar_por_id(empleado_id)
        )

    # =========================================
    # PRUEBAS DE PROYECTOS
    # =========================================

    def test_06_registrar_proyecto(self):
        proyecto_id = self.crear_proyecto()

        proyecto = self.proyectos.buscar_por_id(
            proyecto_id
        )

        self.assertEqual(
            proyecto.nombre, "Proyecto Solar"
        )
        self.assertEqual(proyecto.ciudad, "Chillán")

    def test_07_modificar_proyecto(self):
        proyecto_id = self.crear_proyecto()

        modificado = Proyecto(
            nombre="Proyecto Eólico",
            descripcion="Generación de energía eólica",
            ciudad="Concepción",
            fecha_inicio="2026-12-01",
            fecha_fin="2027-02-28",
            presupuesto_centavos=200000000,
            moneda="CLP",
            estado="en_curso"
        )

        resultado = self.proyectos.modificar(
            proyecto_id, modificado
        )

        actualizado = self.proyectos.buscar_por_id(
            proyecto_id
        )

        self.assertTrue(resultado)
        self.assertEqual(
            actualizado.nombre, "Proyecto Eólico"
        )
        self.assertEqual(
            actualizado.estado, "en_curso"
        )

    def test_08_validar_fechas(self):
        proyecto = Proyecto(
            nombre="Proyecto de prueba",
            descripcion="Validación de fechas",
            ciudad="Chillán",
            fecha_inicio="2027-02-01",
            fecha_fin="2026-12-01",
            presupuesto_centavos=100000,
            moneda="CLP"
        )

        with self.assertRaises(ValueError):
            self.proyectos.registrar(proyecto)

    def test_09_desactivar_reactivar_proyecto(self):
        proyecto_id = self.crear_proyecto()

        self.assertTrue(
            self.proyectos.desactivar(proyecto_id)
        )
        self.assertIsNone(
            self.proyectos.buscar_por_id(proyecto_id)
        )

        self.assertEqual(
            len(self.proyectos.listar_inactivos()), 1
        )

        self.assertTrue(
            self.proyectos.reactivar(proyecto_id)
        )
        self.assertIsNotNone(
            self.proyectos.buscar_por_id(proyecto_id)
        )

    # =========================================
    # PRUEBAS DE ASIGNACIONES
    # =========================================

    def test_10_asignar_empleado(self):
        empleado_id = self.crear_empleado()
        proyecto_id = self.crear_proyecto()

        self.asignaciones.asignar(
            empleado_id, proyecto_id
        )

        asignaciones = self.asignaciones.listar()

        self.assertEqual(len(asignaciones), 1)
        self.assertEqual(
            asignaciones[0].empleado_nombre,
            "Ana Rojas"
        )

    def test_11_impedir_asignacion_duplicada(self):
        empleado_id = self.crear_empleado()
        proyecto_id = self.crear_proyecto()

        self.asignaciones.asignar(
            empleado_id, proyecto_id
        )

        with self.assertRaises(sqlite3.IntegrityError):
            self.asignaciones.asignar(
                empleado_id, proyecto_id
            )

    def test_12_impedir_empleado_inactivo(self):
        empleado_id = self.crear_empleado()
        proyecto_id = self.crear_proyecto()

        self.empleados.desactivar(empleado_id)

        with self.assertRaises(ValueError):
            self.asignaciones.asignar(
                empleado_id, proyecto_id
            )

    def test_13_impedir_proyecto_inactivo(self):
        empleado_id = self.crear_empleado()
        proyecto_id = self.crear_proyecto()

        self.proyectos.desactivar(proyecto_id)

        with self.assertRaises(ValueError):
            self.asignaciones.asignar(
                empleado_id, proyecto_id
            )

    def test_14_filtrar_por_proyecto(self):
        empleado_id = self.crear_empleado()
        proyecto_1 = self.crear_proyecto()
        proyecto_2 = self.crear_proyecto(
            "Proyecto Eólico"
        )

        self.asignaciones.asignar(
            empleado_id, proyecto_1
        )
        self.asignaciones.asignar(
            empleado_id, proyecto_2
        )

        resultado = self.asignaciones.listar(
            proyecto_1
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0].proyecto_id,
            proyecto_1
        )

    def test_15_retirar_asignacion(self):
        empleado_id = self.crear_empleado()
        proyecto_id = self.crear_proyecto()

        asignacion_id = self.asignaciones.asignar(
            empleado_id, proyecto_id
        )

        self.assertTrue(
            self.asignaciones.quitar(asignacion_id)
        )
        self.assertEqual(
            len(self.asignaciones.listar()), 0
        )

        # El empleado y el proyecto siguen existiendo.
        self.assertIsNotNone(
            self.empleados.buscar_por_id(empleado_id)
        )
        self.assertIsNotNone(
            self.proyectos.buscar_por_id(proyecto_id)
        )

    # =========================================
    # PRUEBA DE PERSISTENCIA
    # =========================================

    def test_16_persistencia_sqlite(self):
        empleado_id = self.crear_empleado()
        proyecto_id = self.crear_proyecto()

        # Abrimos una conexión nueva para verificar.
        with closing(base_datos.conectar()) as conexion:
            empleado = conexion.execute(
                "SELECT nombre FROM empleados WHERE id = ?",
                (empleado_id,)
            ).fetchone()

            proyecto = conexion.execute(
                "SELECT nombre FROM proyectos WHERE id = ?",
                (proyecto_id,)
            ).fetchone()

        self.assertEqual(
            empleado["nombre"], "Ana Rojas"
        )
        self.assertEqual(
            proyecto["nombre"], "Proyecto Solar"
        )


if __name__ == "__main__":
    unittest.main()
