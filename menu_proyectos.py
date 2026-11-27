
import sqlite3

from decimal import Decimal, InvalidOperation

from base_datos import inicializar_base_datos
from proyectos import Proyecto, RepositorioProyectos

from servicios_proyectos import (
    consultar_clima_proyecto,
    convertir_presupuesto_proyecto
)

def pedir_campo(etiqueta, valor_actual=None):
    if valor_actual is None:
        texto = input(f"{etiqueta}: ").strip()
    else:
        texto = input(
            f"{etiqueta} [{valor_actual}]: "
        ).strip()

    if texto:
        return texto

    if valor_actual is not None:
        return valor_actual

    return ""

def solicitar_proyecto(actual=None):
    nombre = pedir_campo(
        "Nombre",
        actual.nombre if actual else None
    )

    descripcion = pedir_campo(
        "Descripción",
        actual.descripcion if actual else None
    )

    ciudad = pedir_campo(
        "Ciudad",
        actual.ciudad if actual else None
    )

    inicio = pedir_campo(
        "Fecha inicio (AAAA-MM-DD)",
        actual.fecha_inicio if actual else None
    )

    fin = pedir_campo(
        "Fecha fin (AAAA-MM-DD)",
        actual.fecha_fin if actual else None
    )

    dinero_actual = (
        f"{Decimal(actual.presupuesto_centavos) / 100:.2f}"
        if actual else None
    )

    monto_texto = pedir_campo(
        "Presupuesto (ej. 1500000.00)",
        dinero_actual
    ).replace(",", ".")

    try:
        monto = Decimal(monto_texto)
    except InvalidOperation:
        raise ValueError("Presupuesto inválido.")

    centavos_decimal = monto * 100

    if (
        not monto.is_finite()
        or monto < 0
        or centavos_decimal != centavos_decimal.to_integral_value()
        or centavos_decimal > 9_223_372_036_854_775_807
    ):
        raise ValueError(
            "Presupuesto inválido: máximo dos decimales."
        )

    centavos = int(centavos_decimal)

    moneda = pedir_campo(
        "Moneda (CLP, USD, EUR)",
        actual.moneda if actual else "CLP"
    ).upper()

    estado = pedir_campo(
        "Estado (planificado, en_curso, finalizado)",
        actual.estado if actual else "planificado"
    ).lower()

    proyecto = Proyecto(
        nombre=nombre,
        descripcion=descripcion,
        ciudad=ciudad,
        fecha_inicio=inicio,
        fecha_fin=fin,
        presupuesto_centavos=centavos,
        moneda=moneda,
        estado=estado
    )

    proyecto.validar()

    return proyecto

def mostrar_proyectos(proyectos):
    if not proyectos:
        print("No se encontraron proyectos.")
        return

    for proyecto in proyectos:
        monto = Decimal(
            proyecto.presupuesto_centavos
        ) / 100

        print(
            f"{proyecto.id} | {proyecto.nombre} | "
            f"{proyecto.ciudad} | {proyecto.estado} | "
            f"{monto:.2f} {proyecto.moneda}"
        )


def pedir_id():
    proyecto_id = int(
        input("ID del proyecto: ").strip()
    )

    if proyecto_id <= 0:
        raise ValueError(
            "El ID debe ser un número entero positivo."
        )

    return proyecto_id

def menu_proyectos():
    try:
        inicializar_base_datos()

    except sqlite3.Error:
        print("No se pudo preparar la base de datos.")
        return

    repositorio = RepositorioProyectos()

    while True:
        print("\n=== GESTIÓN DE PROYECTOS ===")
        print("1. Registrar proyecto")
        print("2. Listar proyectos activos")
        print("3. Modificar proyecto")
        print("4. Desactivar proyecto")
        print("5. Reactivar proyecto")
        print("6. Consultar clima de un proyecto")
        print("7. Convertir presupuesto a CLP")
        print("8. Volver al menú privado")

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        try:
            if opcion == "1":
                proyecto = solicitar_proyecto()

                nuevo_id = repositorio.registrar(
                    proyecto
                )

                print(
                    f"Proyecto registrado con ID {nuevo_id}."
                )

            elif opcion == "2":
                mostrar_proyectos(
                    repositorio.listar()
                )

            elif opcion == "3":
                proyecto_id = pedir_id()

                actual = repositorio.buscar_por_id(
                    proyecto_id
                )

                if actual is None:
                    print("Proyecto no encontrado o inactivo.")
                    continue

                print("\n=== DATOS ACTUALES ===")
                mostrar_proyectos([actual])

                print(
                    "\nPresione Enter para conservar "
                    "los valores existentes."
                )

                nuevo = solicitar_proyecto(actual)

                if repositorio.modificar(
                    proyecto_id, nuevo
                ):
                    print("\nProyecto actualizado.")

                    actualizado = (
                        repositorio.buscar_por_id(
                            proyecto_id
                        )
                    )

                    mostrar_proyectos([actualizado])

                else:
                    print("No se pudo actualizar el proyecto.")

            elif opcion == "4":
                proyecto_id = pedir_id()

                if repositorio.desactivar(proyecto_id):
                    print("Proyecto desactivado.")
                else:
                    print("Proyecto no encontrado o ya inactivo.")

            elif opcion == "5":
                inactivos = repositorio.listar_inactivos()

                print("\n=== PROYECTOS DESACTIVADOS ===")
                mostrar_proyectos(inactivos)

                if not inactivos:
                    continue

                proyecto_id = pedir_id()

                if repositorio.reactivar(proyecto_id):
                    print("Proyecto reactivado.")
                else:
                    print("Proyecto no encontrado o ya activo.")


            elif opcion == "6":
                print("\n=== CLIMA DEL PROYECTO ===")

                mostrar_proyectos(repositorio.listar())
                proyecto_id = pedir_id()

                proyecto = repositorio.buscar_por_id(
                    proyecto_id
                )

                if proyecto is None:
                    print("Proyecto no encontrado.")
                    continue

                clima = consultar_clima_proyecto(proyecto)

                print("\n=== RESULTADO CLIMÁTICO ===")
                print("Proyecto:", clima["proyecto"])
                print("Ciudad:", clima["ciudad"])
                print(f"Temperatura: {clima['temperatura']} °C")
                print(f"Humedad: {clima['humedad']} %")
                print(f"Viento: {clima['viento']} km/h")
                print("Estado del tiempo:", clima["estado"])
                print("Fecha y hora:", clima["fecha"])

            elif opcion == "7":
                print("\n=== CONVERTIR PRESUPUESTO ===")

                mostrar_proyectos(repositorio.listar())
                proyecto_id = pedir_id()

                proyecto = repositorio.buscar_por_id(
                    proyecto_id
                )

                if proyecto is None:
                    print("Proyecto no encontrado.")
                    continue

                resultado = convertir_presupuesto_proyecto(
                    proyecto
                )

                print("\n=== RESULTADO DE CONVERSIÓN ===")
                print("Proyecto:", resultado["proyecto"])
                print(
                    f"Presupuesto: {resultado['monto']:.2f} "
                    f"{resultado['moneda']}"
                )
                print(
                    f"Tipo de cambio: {resultado['tasa']} CLP"
                )
                print(
                    f"Equivalente estimado: "
                    f"{resultado['equivalente_clp']:.0f} CLP"
                )
                print("Actualización:", resultado["fecha"])
                print("Valor referencial, no bancario.")

            elif opcion == "8":
                print("Regresando al menú privado...")
                break


            else:
                print("Opción no válida.")

        except ValueError as error:
            print(f"Dato inválido: {error}")

        except sqlite3.Error:
            print(
                "Problema de base de datos. "
                "No fue posible completar la operación."
            )
        except OSError:
            print(
                "Error de conexión con el servicio externo. "
                "Intente nuevamente más tarde."
            )
