# EcoTech Solutions

## 1. Descripción del proyecto

EcoTech Solutions es un sistema desarrollado en Python que permite consultar información externa mediante APIs, incorporando mecanismos de seguridad para proteger el acceso y los datos de los usuarios.

El programa permite consultar las condiciones climáticas de ciudades de Chile y obtener tipos de cambio internacionales para realizar conversiones referenciales a pesos chilenos.

Este proyecto fue desarrollado como parte de la Evaluación Sumativa 3 de la asignatura Programación Orientada a Objeto Seguro.

## 2. Funcionalidades del sistema

**Registro e inicio de sesión**

El sistema permite registrar usuarios, validar sus credenciales e iniciar sesión. Las contraseñas se almacenan mediante hashes generados con PBKDF2-HMAC-SHA256 y un salt aleatorio.

**Consulta del clima**

Mediante la API Open-Meteo, el usuario puede consultar información meteorológica de ciudades chilenas, incluyendo temperatura, humedad, velocidad del viento y estado del tiempo.

**Consulta de tipos de cambio**

Mediante ExchangeRate-API, el sistema permite consultar los valores del dólar estadounidense (USD) y del euro (EUR) y convertir montos a pesos chilenos (CLP).

Los resultados son referenciales y muestran la fecha de actualización de la información.

**Validación de datos**

Se comprueban los datos ingresados por el usuario, incluyendo nombres de usuario, contraseñas, ciudades, monedas y montos. Esto permite rechazar entradas incorrectas antes de procesarlas.

**Manejo de errores**

Se implementaron estructuras `try/except` para controlar problemas de conexión, respuestas inválidas y errores HTTP, como 400, 404, 429 y 500, evitando interrupciones inesperadas en los casos contemplados.

**Control de acceso**

Las funcionalidades de consulta del clima y tipos de cambio se encuentran disponibles únicamente después de iniciar sesión correctamente.

## 3. Tecnologías utilizadas

El proyecto utiliza Python 3 y bibliotecas de su biblioteca estándar:

- `urllib`: conexión con servicios externos mediante HTTPS.
- `json`: lectura y almacenamiento de datos JSON.
- `hashlib`: generación de hashes para proteger contraseñas.
- `secrets`: generación de valores aleatorios seguros y comparación de hashes.
- `getpass`: ingreso de contraseñas sin mostrarlas en pantalla.
- `re`: validación de entradas mediante expresiones regulares.
- `decimal`: cálculos de conversión monetaria con mayor precisión decimal.
- `unittest`: ejecución de pruebas automáticas.
- `pathlib`: manejo de rutas de archivos.

APIs utilizadas:

- Open-Meteo: https://open-meteo.com/
- ExchangeRate-API: https://www.exchangerate-api.com/

## 4. Estructura del proyecto

**main.py:** contiene el menú principal y el menú privado.

**seguridad.py:** permite registrar usuarios, almacenar hashes de contraseñas y verificar credenciales.

**validaciones.py:** contiene las funciones para validar usuarios, contraseñas y ciudades.

**clima.py:** realiza las consultas meteorológicas mediante Open-Meteo.

**monedas.py:** obtiene tipos de cambio y realiza conversiones a pesos chilenos.

**errores_api.py:** contiene mensajes para gestionar diferentes códigos de error HTTP.

**test_ecotech.py:** contiene las pruebas automáticas del sistema.

**ANALISIS_SEGURIDAD_IA.md:** documenta las medidas de seguridad, los errores encontrados, las decisiones técnicas y el uso de inteligencia artificial durante el desarrollo.

**.gitignore:** identifica archivos locales que no deben incluirse en el repositorio.

## 5. Requisitos de ejecución

Para ejecutar el programa es necesario tener instalado Python 3 y disponer de conexión a Internet para consultar las APIs.

El proyecto utiliza bibliotecas incluidas en Python, por lo que no requiere instalar paquetes adicionales.

## 6. Ejecución del programa

Abrir la carpeta del proyecto en Visual Studio Code e ingresar el siguiente comando en la terminal:

`py main.py`

El programa mostrará un menú con las siguientes opciones:

1. Registrar usuario.
2. Iniciar sesión.
3. Salir.

Después de iniciar sesión correctamente, se habilitará el menú privado:

1. Consultar clima.
2. Consultar tipo de cambio.
3. Cerrar sesión.

## 7. Pruebas automáticas

Se implementaron pruebas automáticas mediante `unittest` para comprobar las validaciones, el registro de usuarios, la autenticación, el procesamiento de respuestas y el manejo de errores HTTP.

Para ejecutar las pruebas se debe utilizar:

`py -m unittest -v test_ecotech`

El resultado esperado es que todas las pruebas finalicen correctamente, mostrando el mensaje `OK`.

**Cantidad de pruebas aprobadas:20/20**

## 8. Medidas de seguridad

Durante el desarrollo se incorporaron diferentes mecanismos para mejorar la protección del sistema:

- Almacenamiento de contraseñas mediante hash y salt aleatorio.
- Validación de credenciales antes de autorizar el acceso.
- Restricción de las consultas a usuarios autenticados.
- Validación de entradas antes de procesar solicitudes.
- Manejo de excepciones y errores HTTP.
- Uso de mensajes de error que evitan exponer información técnica innecesaria.
- Exclusión del archivo de usuarios de la carpeta de entrega.

El archivo `usuarios.json` se genera localmente al registrar usuarios y no debe incluirse en la entrega cuando contiene información real.

## 9. Uso de inteligencia artificial

Durante el desarrollo se utilizó ChatGPT como herramienta de apoyo para comprender funciones, identificar errores, analizar posibles vulnerabilidades y proponer mejoras.

Las sugerencias fueron revisadas mediante la ejecución del programa y pruebas en Visual Studio Code.

Entre las correcciones realizadas se encuentran los ajustes en la validación de respuestas de APIs, la presentación de conversiones monetarias y el tratamiento de errores.

Las decisiones técnicas y las evidencias del proceso se encuentran documentadas en `ANALISIS_SEGURIDAD_IA.md`.

## 10. Limitaciones del proyecto

El sistema corresponde a un prototipo académico.

La consulta meteorológica está limitada a ciudades de Chile y la conversión monetaria admite USD y EUR hacia CLP.

Los tipos de cambio se utilizan únicamente con fines referenciales y no representan cotizaciones bancarias garantizadas.

El sistema requiere conexión a Internet para obtener información actualizada de los servicios externos.

## 11. Conclusión

El desarrollo de EcoTech Solutions permitió aplicar conocimientos de programación en Python, consumo de APIs, procesamiento de JSON y mecanismos de seguridad.

También permitió comprender la importancia de validar la información, proteger las credenciales y controlar los errores para mantener la estabilidad del programa.

La implementación de pruebas automáticas y el análisis del código con apoyo de inteligencia artificial contribuyeron a detectar problemas y mejorar progresivamente el funcionamiento del sistema.