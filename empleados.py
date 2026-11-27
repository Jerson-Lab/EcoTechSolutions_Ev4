import re
import sqlite3

from dataclasses import dataclass
from contextlib import closing

from base_datos import conectar

@dataclass
class Empleado:
    nombre: str
    cargo: str
    correo: str
    id: int | None = None
    activo: bool = True

    def validar(self):
        self.nombre = " ".join(self.nombre.strip().split())
        self.cargo = " ".join(self.cargo.strip().split())
        self.correo = self.correo.strip().lower()

        if not 2 <= len(self.nombre) <= 80:
            raise ValueError("Nombre inválido.")

        if not re.fullmatch(
            r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ ]+",
            self.nombre
        ):
            raise ValueError("El nombre contiene caracteres inválidos.")

        if not 2 <= len(self.cargo) <= 60:
            raise ValueError("Cargo inválido.")

        patron_correo = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        if (
            len(self.correo) > 254
            or not re.fullmatch(patron_correo, self.correo)
        ):
            raise ValueError("Correo electrónico inválido.")

class RepositorioEmpleados:
    def registrar(self, empleado):
        empleado.validar()

        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    INSERT INTO empleados
                    (nombre, cargo, correo)
                    VALUES (?,?,?)
                    """,
                    (
                        empleado.nombre,
                        empleado.cargo,
                        empleado.correo
                    )
                )

                return cursor.lastrowid

    def listar(self):
        with closing(conectar()) as conexion:
            filas = conexion.execute(
                """
                SELECT id, nombre, cargo, correo, activo
                FROM empleados
                WHERE activo = 1
                ORDER BY id
                """
            ).fetchall()

        return [
            Empleado(
                id=fila["id"],
                nombre=fila["nombre"],
                cargo=fila["cargo"],
                correo=fila["correo"],
                activo=bool(fila["activo"])
            )
            for fila in filas
        ]

    def buscar_por_id(self, empleado_id):
        with closing(conectar()) as conexion:
            fila = conexion.execute(
                """
                SELECT id, nombre, cargo, correo, activo
                FROM empleados
                WHERE id = ? AND activo = 1
                """,
                (empleado_id,)
            ).fetchone()

        if fila is None:
            return None

        return Empleado(
            id=fila["id"],
            nombre=fila["nombre"],
            cargo=fila["cargo"],
            correo=fila["correo"],
            activo=bool(fila["activo"])
        )

    def modificar(self, empleado_id, empleado):
        empleado.validar()

        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    UPDATE empleados
                    SET nombre = ?,
                        cargo = ?,
                        correo = ?
                    WHERE id = ? AND activo = 1
                    """,
                    (
                        empleado.nombre,
                        empleado.cargo,
                        empleado.correo,
                        empleado_id
                    )
                )

                return cursor.rowcount > 0

    def desactivar(self, empleado_id):
        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    UPDATE empleados
                    SET activo = 0
                    WHERE id = ? AND activo = 1
                    """,
                    (empleado_id,)
                )

                return cursor.rowcount > 0

    def listar_inactivos(self):
        with closing(conectar()) as conexion:
            filas = conexion.execute(
                """
                SELECT id, nombre, cargo, correo, activo
                FROM empleados
                WHERE activo = 0
                ORDER BY id
                """
            ).fetchall()

        return [
            Empleado(
                id=fila["id"],
                nombre=fila["nombre"],
                cargo=fila["cargo"],
                correo=fila["correo"],
                activo=bool(fila["activo"])
            )
            for fila in filas
        ]

    def reactivar(self, empleado_id):
        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    UPDATE empleados
                    SET activo = 1
                    WHERE id = ? AND activo = 0
                    """,
                    (empleado_id,)
                )

                return cursor.rowcount > 0

