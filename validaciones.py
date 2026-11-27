import re 

def validar_usuario(usuario):
    patron = r"[a-zA-Z0-9_]{3,20}"

    return bool(re.fullmatch(patron, usuario))

def validar_contrasena(contrasena):
    largo_valido = 10 <= len(contrasena) <= 128
    tiene_letra = any(c.isalpha() for c in contrasena)
    tiene_numero = any(c.isdigit() for c in contrasena)

    return largo_valido and tiene_letra and tiene_numero

def validar_ciudad(ciudad):
    patron = r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ ]{2,60}"

    return bool(re.fullmatch(patron, ciudad))
