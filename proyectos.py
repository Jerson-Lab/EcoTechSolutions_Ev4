
import sqlite3

from dataclasses import dataclass
from datetime import date
from contextlib import closing

from base_datos import conectar

@dataclass
class Proyecto:
    nombre: str
    descripcion: str
    ciudad: str
    fecha_inicio: str
    fecha_fin: str
    presupuesto_centavos: int
    moneda: str
    estado: str = "planificado"
    id: int | None = None
    activo: bool = True

    def validar(self):
        self.nombre = self.nombre.strip()
        self.descripcion = self.descripcion.strip()
        self.ciudad = self.ciudad.strip()
        self.moneda = self.moneda.strip().upper()

        if not 3 <= len(self.nombre) <= 100:
            raise ValueError("Nombre del proyecto inválido.")

        if len(self.descripcion) > 500:
            raise ValueError("Descripción demasiado extensa.")

        if not 2 <= len(self.ciudad) <= 80:
            raise ValueError("Ciudad inválida.")

        try:
            inicio = date.fromisoformat(self.fecha_inicio)
            fin = date.fromisoformat(self.fecha_fin)
        except ValueError:
            raise ValueError("Las fechas deben ser válidas.")

        if fin < inicio:
            raise ValueError(
                "La fecha de término no puede ser anterior al inicio."
            )

        if (
            type(self.presupuesto_centavos) is not int
            or self.presupuesto_centavos < 0
        ):
            raise ValueError("Presupuesto inválido.")

        if self.moneda not in ("CLP", "USD", "EUR"):
            raise ValueError("Moneda no permitida.")

        if self.estado not in (
            "planificado",
            "en_curso",
            "finalizado"
        ):
            raise ValueError("Estado de proyecto inválido.")

class RepositorioProyectos:

    def registrar(self, proyecto):
        proyecto.validar()

        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    INSERT INTO proyectos (
                        nombre,
                        descripcion,
                        ciudad,
                        fecha_inicio,
                        fecha_fin,
                        presupuesto_centavos,
                        moneda,
                        estado
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        proyecto.nombre,
                        proyecto.descripcion,
                        proyecto.ciudad,
                        proyecto.fecha_inicio,
                        proyecto.fecha_fin,
                        proyecto.presupuesto_centavos,
                        proyecto.moneda,
                        proyecto.estado
                    )
                )

                return cursor.lastrowid

    def listar(self):
        with closing(conectar()) as conexion:
            filas = conexion.execute(
                """
                SELECT *
                FROM proyectos
                WHERE activo = 1
                ORDER BY id
                """
            ).fetchall()

        return [self._convertir(fila) for fila in filas]

    def buscar_por_id(self, proyecto_id):
        with closing(conectar()) as conexion:
            fila = conexion.execute(
                """
                SELECT *
                FROM proyectos
                WHERE id = ? AND activo = 1
                """,
                (proyecto_id,)
            ).fetchone()

        if fila is None:
            return None

        return self._convertir(fila)

    def _convertir(self, fila):
        return Proyecto(
            id=fila["id"],
            nombre=fila["nombre"],
            descripcion=fila["descripcion"] or "",
            ciudad=fila["ciudad"],
            fecha_inicio=fila["fecha_inicio"],
            fecha_fin=fila["fecha_fin"],
            presupuesto_centavos=fila["presupuesto_centavos"],
            moneda=fila["moneda"],
            estado=fila["estado"],
            activo=bool(fila["activo"])
        )

    def modificar(self, proyecto_id, proyecto):
        proyecto.validar()

        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    UPDATE proyectos
                    SET nombre = ?,
                        descripcion = ?,
                        ciudad = ?,
                        fecha_inicio = ?,
                        fecha_fin = ?,
                        presupuesto_centavos = ?,
                        moneda = ?,
                        estado = ?
                    WHERE id = ? AND activo = 1
                    """,
                    (
                        proyecto.nombre,
                        proyecto.descripcion,
                        proyecto.ciudad,
                        proyecto.fecha_inicio,
                        proyecto.fecha_fin,
                        proyecto.presupuesto_centavos,
                        proyecto.moneda,
                        proyecto.estado,
                        proyecto_id
                    )
                )

                actualizado = cursor.rowcount > 0

        return actualizado

    def desactivar(self, proyecto_id):
        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    UPDATE proyectos
                    SET activo = 0
                    WHERE id = ? AND activo = 1
                    """,
                    (proyecto_id,)
                )

                cambiado = cursor.rowcount > 0

        return cambiado

    def listar_inactivos(self):
        with closing(conectar()) as conexion:
            filas = conexion.execute(
                """
                SELECT *
                FROM proyectos
                WHERE activo = 0
                ORDER BY id
                """
            ).fetchall()

        return [self._convertir(fila) for fila in filas]

    def reactivar(self, proyecto_id):
        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    UPDATE proyectos
                    SET activo = 1
                    WHERE id = ? AND activo = 0
                    """,
                    (proyecto_id,)
                )

                cambiado = cursor.rowcount > 0

        return cambiado

    def reactivar(self, proyecto_id):
        with closing(conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    UPDATE proyectos
                    SET activo = 1
                    WHERE id = ? AND activo = 0
                    """,
                    (proyecto_id,)
                )

                cambiado = cursor.rowcount > 0

        return cambiado
