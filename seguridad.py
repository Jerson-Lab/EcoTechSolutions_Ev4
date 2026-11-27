import json
import hashlib
import secrets
import getpass

from pathlib import Path
from validaciones import validar_usuario, validar_contrasena

RUTA_USUARIOS = Path(__file__).with_name("usuarios.json")
ITERACIONES = 600_000

def cargar_usuarios():
    if not RUTA_USUARIOS.exists():
        return {}

    try:
        with open(RUTA_USUARIOS, "r", encoding="utf-8") as archivo:
            usuarios = json.load(archivo)

        if not isinstance(usuarios, dict):
            print("Error: formato de usuarios incorrecto.")
            return None

        return usuarios

    except (OSError, json.JSONDecodeError, UnicodeError):
        print("Error al cargar los usuarios registrados.")
        return None

def registrar_usuario():
    print("\n=== REGISTRO DE USUARIOS ===")

    usuario = input("Ingrese un nombre de usuario: ").strip()

    if not validar_usuario(usuario):
        print("Usuario invlaido. Use entre 3 y 20 caracteres.")
        return

    usuarios = cargar_usuarios()
    if usuarios is None:
        return

    if usuario in usuarios:
        print("Este nombre de usuario ya esta registrado.")
        return

    contrasena = getpass.getpass("Ingrese una contraseña: ")

    if not validar_contrasena(contrasena):
        print("La contraseña debe tener al menos 10 caracteres,")
        print("una letra y un numero, y no superar 128 caracteres.")
        return

    confirmar = getpass.getpass("Confirme su contraseña: ")

    if contrasena != confirmar:
        print("Las contraseñas no coinciden.")
        return

    salt = secrets.token_bytes(16)

    hash_contrasena = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        salt,
        ITERACIONES
    )

    usuarios[usuario] = {
        "salt": salt.hex(),
        "hash": hash_contrasena.hex(),
        "iteraciones": ITERACIONES
    }

    with open(RUTA_USUARIOS, "w", encoding="utf-8") as archivo:
        json.dump(usuarios, archivo, indent=4)

    print("Usuario registrado correctamente")

def iniciar_sesion():
    print("\n=== INICIO DE SESIÓN ===")

    usuarios = cargar_usuarios()
    if usuarios is None:
        return None

    for intento in range(1, 4):
        usuario = input("Nombre de usuario: ").strip()
        contrasena = getpass.getpass("Contraseña: ")

        if not validar_usuario(usuario):
            print("Usuario o contraseña incorrectos.")
            continue

        datos = usuarios.get(usuario)

        if datos is None:
            print("Usuario o contraseña incorrectos.")
            continue

        try:
            salt = bytes.fromhex(datos["salt"])
            hash_guardado = bytes.fromhex(datos["hash"])
            iteraciones = datos["iteraciones"]

            if not isinstance(iteraciones, int):
                raise ValueError("Iteraciones inválidas")

            if not 100_000 <= iteraciones <= 2_000_000:
                raise ValueError("Iteraciones fuera de rango")

            hash_ingresado = hashlib.pbkdf2_hmac(
                "sha256",
                contrasena.encode("utf-8"),
                salt,
                iteraciones
            )

            acceso_valido = secrets.compare_digest(
                hash_ingresado,
                hash_guardado
            )

        except (KeyError, ValueError,TypeError):
            print("Error en los dato de autenticación")
            return None

        if acceso_valido:
            print("\nInicio de sesión exitoso.")
            print(f"Bienvenido, {usuario}")
            return usuario

        print("Usuario o contraseña incorrectos.")
        print(f"Intento {intento} de 3")

    print("\nSe aclanzó el máximo de intentos. ")
    return None