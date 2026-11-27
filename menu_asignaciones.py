
import sqlite3

from base_datos import inicializar_base_datos
from empleados import RepositorioEmpleados
from proyectos import RepositorioProyectos
from asignaciones import RepositorioAsignaciones


def pedir_id(mensaje):
    numero = int(input(mensaje).strip())

    if numero <= 0:
        raise ValueError("El ID debe ser positivo.")

    return numero


def mostrar_asignaciones(asignaciones):
    if not asignaciones:
        print("No se encontraron asignaciones.")
        return

    for a in asignaciones:
        print(
            f"Asignación #{a.id} | "
            f"Empleado: {a.empleado_nombre} "
            f"(ID {a.empleado_id}) | "
            f"Proyecto: {a.proyecto_nombre} "
            f"(ID {a.proyecto_id})"
        )

def menu_asignaciones():
    try:
        inicializar_base_datos()

    except sqlite3.Error:
        print("No se pudo preparar la base de datos.")
        return

    repositorio = RepositorioAsignaciones()
    empleados_repo = RepositorioEmpleados()
    proyectos_repo = RepositorioProyectos()

    while True:
        print("\n=== ASIGNACIONES DE EMPLEADOS ===")
        print("1. Asignar empleado a proyecto")
        print("2. Listar todas las asignaciones")
        print("3. Consultar empleados de un proyecto")
        print("4. Retirar empleado de un proyecto")
        print("5. Volver al menú privado")

        opcion = input("Seleccione una opción: ").strip()

        try:
            if opcion == "1":
                empleados = empleados_repo.listar()
                proyectos = proyectos_repo.listar()

                if not empleados or not proyectos:
                    print(
                        "Se necesitan empleados y proyectos "
                        "activos para realizar una asignación."
                    )
                    continue

                print("\n=== EMPLEADOS ACTIVOS ===")

                for e in empleados:
                    print(f"{e.id} - {e.nombre}")

                print("\n=== PROYECTOS ACTIVOS ===")

                for p in proyectos:
                    print(f"{p.id} - {p.nombre}")

                empleado_id = pedir_id(
                    "\nID del empleado: "
                )

                proyecto_id = pedir_id(
                    "ID del proyecto: "
                )

                nuevo_id = repositorio.asignar(
                    empleado_id, proyecto_id
                )

                print(
                    f"Asignación registrada con ID {nuevo_id}."
                )

            elif opcion == "2":
                mostrar_asignaciones(
                    repositorio.listar()
                )

            elif opcion == "3":
                proyecto_id = pedir_id(
                    "ID del proyecto: "
                )

                proyecto = proyectos_repo.buscar_por_id(
                    proyecto_id
                )

                if proyecto is None:
                    print("Proyecto no encontrado o inactivo.")
                    continue

                print(f"\nProyecto: {proyecto.nombre}")

                mostrar_asignaciones(
                    repositorio.listar(proyecto_id)
                )

            elif opcion == "4":
                asignaciones = repositorio.listar()

                mostrar_asignaciones(asignaciones)

                if not asignaciones:
                    continue

                asignacion_id = pedir_id(
                    "\nID de la asignación a retirar: "
                )

                confirmacion = input(
                    "¿Confirmar retiro? (s/n): "
                ).strip().lower()

                if confirmacion != "s":
                    print("Operación cancelada.")
                    continue

                if repositorio.quitar(asignacion_id):
                    print("Asignación retirada correctamente.")
                else:
                    print("Asignación no encontrada.")

            elif opcion == "5":
                print("Regresando al menú privado...")
                break

            else:
                print("Opción no válida.")

        except ValueError as error:
            print(f"Dato inválido: {error}")

        except sqlite3.IntegrityError:
            print(
                "No se pudo realizar la asignación. "
                "Puede que el empleado ya esté asignado "
                "a ese proyecto."
            )

        except sqlite3.Error:
            print("Ocurrió un error con la base de datos.")
