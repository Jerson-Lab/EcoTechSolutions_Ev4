
import sqlite3

from pathlib import Path
from contextlib import closing


RUTA_BD = Path(__file__).with_name("ecotech.db")


def conectar():
    conexion = sqlite3.connect(RUTA_BD)

    conexion.row_factory = sqlite3.Row

    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion

def inicializar_base_datos():

    with closing(conectar()) as conexion:

        with conexion:
            conexion.executescript("""
                CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cargo TEXT NOT NULL,
                    correo TEXT NOT NULL UNIQUE,
                    activo INTEGER NOT NULL DEFAULT 1
                        CHECK (activo IN (0, 1))
                );

                CREATE TABLE IF NOT EXISTS proyectos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    ciudad TEXT NOT NULL,
                    fecha_inicio TEXT NOT NULL,
                    fecha_fin TEXT NOT NULL,
                    presupuesto_centavos INTEGER NOT NULL
                        CHECK (presupuesto_centavos >= 0),
                    moneda TEXT NOT NULL
                        CHECK (moneda IN ('CLP', 'USD', 'EUR')),
                    estado TEXT NOT NULL DEFAULT 'planificado'
                        CHECK (estado IN (
                            'planificado',
                            'en_curso',
                            'finalizado'
                        )),
                    activo INTEGER NOT NULL DEFAULT 1
                        CHECK (activo IN (0, 1)),
                    CHECK (fecha_fin >= fecha_inicio)
                );

                CREATE TABLE IF NOT EXISTS asignaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    proyecto_id INTEGER NOT NULL,

                    UNIQUE (empleado_id, proyecto_id),

                    FOREIGN KEY (empleado_id)
                        REFERENCES empleados(id),

                    FOREIGN KEY (proyecto_id)
                        REFERENCES proyectos(id)
                );
            """)

    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":

    inicializar_base_datos()

    with closing(conectar()) as conexion:

        cursor = conexion.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN (
                  'empleados',
                  'proyectos',
                  'asignaciones'
              )
            ORDER BY name
        """)

        print("\nTablas creadas:")

        for tabla in cursor:
            print("-", tabla["name"])
