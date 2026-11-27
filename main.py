from seguridad import registrar_usuario, iniciar_sesion
from clima import consultar_clima
from monedas import consultar_tipo_cambio

def mostrar_menu():
    print("\n=== ECOTECH SOLUTIONS ===")
    print("1. Registrar usuario")
    print("2. Iniciar sesión")
    print("3. Salir")

def menu_privado(usuario):
    while True:
        print("\n=== PANEL ECOTECH SOLUTIONS ===")
        print(f"Usuario conectado: {usuario}")

        print("\n1. Consultar clima")
        print("2.Consultar tipo de cambio")
        print("3. Cerrar Sesión")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            consultar_clima()

        elif opcion == "2":
            consultar_tipo_cambio()

        elif opcion == "3":
            print("Sesión cerrada correctamente.")
            break
        
        else:
            print("Opción no válida.")
        
def main():
    while True:
        mostrar_menu()

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            registrar_usuario()

        elif opcion == "2":
            usuario = iniciar_sesion()

            if usuario is not None:
                menu_privado(usuario)

        elif opcion == "3":
            print("Saliendo del sistema...")
            break

        else:
            print("Opcion no valida. Intente nuevamente")

if __name__ == "__main__":
    main()