def mensaje_error_http(codigo):
    if codigo == 400:
        return "HTTP 400: Solicitud incorrecta."
    
    elif codigo == 401 or codigo == 403:
        return "HTTP: El servicio rechazó el acceso."
    elif codigo == 404:
        return "HTTP 404:Recurso no encondtrado."
    elif codigo == 429:
        return "HTTP 429: Demasiadas consultas. Intente más tarde"
    elif 500 <= codigo <= 599:
        return f"HTTP {codigo}: Problema del servidor externo."

    else:
        return f"HTTP {codigo}: No se pudo completar la consulta."
