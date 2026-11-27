
import sqlite3

from dataclasses import dataclass
from contextlib import closing

from base_datos import conectar


@dataclass
class Asignacion:
    id: int
    empleado_id: int
    empleado_nombre: str
    proyecto_id: int
    proyecto_nombre: str

class RepositorioAsignaciones:

    def asignar(self, empleado_id, proyecto_id):
        if (
            type(empleado_id) is not int
            or type(proyecto_id) is not int
            or empleado_id <= 0
            or proyecto_id <= 0
        ):
            raise ValueError("Los ID deben ser positivos.")

        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    INSERT INTO asignaciones
                        (empleado_id, proyecto_id)
                    SELECT ?, ?
                    WHERE EXISTS (
                        SELECT 1 FROM empleados
                        WHERE id = ? AND activo = 1
                    )
                    AND EXISTS (
                        SELECT 1 FROM proyectos
                        WHERE id = ? AND activo = 1
                    )
                    """,
                    (
                        empleado_id,
                        proyecto_id,
                        empleado_id,
                        proyecto_id
                    )
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "El empleado o proyecto no existe "
                        "o está desactivado."
                    )

                nuevo_id = cursor.lastrowid

        return nuevo_id

    def listar(self, proyecto_id=None):
        consulta = """
            SELECT
                a.id,
                a.empleado_id,
                e.nombre AS empleado_nombre,
                a.proyecto_id,
                p.nombre AS proyecto_nombre
            FROM asignaciones a
            JOIN empleados e
                ON e.id = a.empleado_id
            JOIN proyectos p
                ON p.id = a.proyecto_id
            WHERE e.activo = 1
              AND p.activo = 1
        """

        parametros = ()

        if proyecto_id is not None:
            consulta += " AND a.proyecto_id = ?"
            parametros = (proyecto_id,)

        consulta += " ORDER BY p.nombre, e.nombre"

        with closing(conectar()) as conexion:
            filas = conexion.execute(
                consulta, parametros
            ).fetchall()

        return [
            Asignacion(
                id=fila["id"],
                empleado_id=fila["empleado_id"],
                empleado_nombre=fila["empleado_nombre"],
                proyecto_id=fila["proyecto_id"],
                proyecto_nombre=fila["proyecto_nombre"]
            )
            for fila in filas
        ]

    def quitar(self, asignacion_id):
        if (
            type(asignacion_id) is not int
            or asignacion_id <= 0
        ):
            raise ValueError("ID de asignación inválido.")

        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    DELETE FROM asignaciones
                    WHERE id = ?
                    """,
                    (asignacion_id,)
                )

                eliminado = cursor.rowcount > 0

        return eliminado
