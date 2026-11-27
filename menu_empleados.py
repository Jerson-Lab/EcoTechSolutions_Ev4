
import sqlite3

from base_datos import inicializar_base_datos
from empleados import Empleado, RepositorioEmpleados


def solicitar_datos():
    nombre = input("Nombre: ")
    cargo = input("Cargo: ")
    correo = input("Correo electrónico: ")

    return Empleado(nombre, cargo, correo)


def menu_empleados():
    try:
        inicializar_base_datos()
    except sqlite3.Error:
        print("No se pudo inicializar la base de datos.")
        return

    repositorio = RepositorioEmpleados()

    while True:
        print("\n=== GESTIÓN DE EMPLEADOS ===")
        print("1. Registrar empleado")
        print("2. Listar empleados")
        print("3. Modificar empleado")
        print("4. Desactivar empleado")
        print("5. Reactivar empleado")
        print("6. Volver al menú privado")

        opcion = input("Seleccione una opción: ").strip()

        try:
            if opcion == "1":
                empleado = solicitar_datos()
                nuevo_id = repositorio.registrar(empleado)
                print(f"Empleado registrado con ID {nuevo_id}.")

            elif opcion == "2":
                empleados = repositorio.listar()

                if not empleados:
                    print("No hay empleados activos.")

                for empleado in empleados:
                    print(
                        f"{empleado.id} - {empleado.nombre} "
                        f"| {empleado.cargo} | {empleado.correo}"
                    )


            elif opcion == "3":
                empleado_id = int(input("ID del empleado: "))

                empleado_actual = repositorio.buscar_por_id(empleado_id)

                if empleado_actual is None:
                    print("Empleado no encontrado.")
                    continue

                print("\n=== DATOS ACTUALES ===")
                print(f"Nombre: {empleado_actual.nombre}")
                print(f"Cargo: {empleado_actual.cargo}")
                print(f"Correo: {empleado_actual.correo}")

                print("\n=== INGRESE LOS NUEVOS DATOS ===")
                empleado_nuevo = solicitar_datos()

                actualizado = repositorio.modificar(
                    empleado_id,
                    empleado_nuevo
                )

                if actualizado:
                    print("\nEmpleado actualizado correctamente.")

                    empleado_actualizado = repositorio.buscar_por_id(
                        empleado_id
                    )

                    print("\n=== DATOS ACTUALIZADOS ===")
                    print(f"Nombre: {empleado_actualizado.nombre}")
                    print(f"Cargo: {empleado_actualizado.cargo}")
                    print(f"Correo: {empleado_actualizado.correo}")

                else:
                    print("No fue posible modificar el empleado.")

            elif opcion == "4":
                empleado_id = int(input("ID del empleado: "))

                if repositorio.desactivar(empleado_id):
                    print("Empleado desactivado correctamente.")
                else:
                    print("Empleado no encontrado.")


            elif opcion == "5":
                inactivos = repositorio.listar_inactivos()

                if not inactivos:
                    print("No hay empleados desactivados.")
                    continue

                print("\n=== EMPLEADOS DESACTIVADOS ===")

                for empleado in inactivos:
                    print(
                        f"{empleado.id} - {empleado.nombre} "
                        f"| {empleado.cargo}"
                    )

                empleado_id = int(
                    input("\nID del empleado a reactivar: ")
                )

                if repositorio.reactivar(empleado_id):
                    print("Empleado reactivado correctamente.")
                else:
                    print("Empleado no encontrado o ya está activo.")

            elif opcion == "6":
                print("Regresando al menú privado...")
                break


            else:
                print("Opción no válida.")

        except ValueError as error:
            print(f"Datos inválidos: {error}")

        except sqlite3.IntegrityError:
            print("No se pudo guardar: el correo ya existe o hay datos duplicados.")

        except sqlite3.Error:
            print("Ocurrió un problema con la base de datos.")
