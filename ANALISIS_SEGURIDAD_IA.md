# Análisis de seguridad y uso de inteligencia artificial
## Proyecto EcoTech Solutions

### 1. Descripción del proyecto

EcoTech Solutions es un sistema desarrollado en Python que permite consultar información meteorológica y tipos de cambio mediante servicios externos. Para proteger estas funcionalidades, se implementó un sistema de registro e inicio de sesión, junto con validaciones de datos y mecanismos de manejo de errores.

Durante el desarrollo se utilizó ChatGPT como herramienta de apoyo para comprender instrucciones, revisar fragmentos de código y encontrar soluciones a problemas de funcionamiento. Las modificaciones se implementaron y probaron en Visual Studio Code.

### 2. Análisis de seguridad

**Protección de contraseñas**

Se implementó el algoritmo PBKDF2-HMAC-SHA256 para almacenar las contraseñas mediante hashes. También se incorporó un salt aleatorio para cada usuario. Esta decisión evita almacenar las contraseñas originales en el archivo JSON.

**Autenticación y control de acceso**

Se desarrolló un sistema de inicio de sesión que comprueba las credenciales antes de permitir el acceso a las consultas. También se estableció un máximo de tres intentos por proceso de inicio de sesión, aunque este límite se reinicia cuando se vuelve a iniciar el procedimiento.

**Validación de entradas**

Se incorporaron funciones que comprueban los nombres de usuario, las contraseñas y las ciudades. Para las consultas monetarias se restringieron las opciones a USD y EUR y se validaron los montos ingresados.

**Manejo de errores HTTP**

Se agregaron estructuras try/except para controlar errores de conexión y respuestas HTTP, incluyendo códigos como 404, 429 y 500. Esto permite mostrar mensajes comprensibles y regresar al menú del programa sin provocar una interrupción inesperada.

### 3. Problemas encontrados y soluciones
1. Comparacion incorrecta del valor success en la API de monedas: Se realizo una correccion de texto ya que estaba escrita como 'succes' en vez de "success"

2. Validación de datos antes de consultar APIs: Se incorporaron funciones de validación y restricciones de entrada

3. Riesgo de exponer detalles tecnicos ante errores: Se utilizaron mensajes de error controlados y excepciones especificas

4. Riesgo de compartir datos de usuario: Se configuro .gitignore y se excluyo el archivo usuarios.json de la entrega
### 4. Uso crítico de inteligencia artificial

La inteligencia artificial se utilizó como apoyo durante la programación y depuración del sistema. Se consultaron explicaciones sobre autenticación, consumo de APIs, procesamiento de JSON y manejo de excepciones.

Las sugerencias se revisaron mediante pruebas prácticas. Por ejemplo, durante la implementación de la API de monedas se detectaron errores que impedían procesar correctamente las respuestas. Estos problemas se identificaron a través de mensajes de diagnóstico y posteriormente se corrigieron.

También se incorporaron pruebas automáticas para comprobar el funcionamiento de las validaciones, la autenticación, las consultas y el manejo de errores.

### 5. Justificación de las decisiones técnicas

Se utilizaron bibliotecas de Python como `urllib`, `json`, `hashlib` y `secrets`, evitando dependencias externas innecesarias.

La separación del programa en distintos módulos facilita el mantenimiento del código. Las funcionalidades de seguridad, validación, clima, monedas y manejo de errores se encuentran organizadas en archivos independientes.

Para los cálculos de monedas se utilizó `Decimal`, con el objetivo de evitar problemas de precisión asociados a los números de punto flotante.

### 6. Pruebas realizadas

El sistema fue probado manualmente mediante registros de usuarios, inicios de sesión, consultas de ciudades y conversiones monetarias.

También se desarrollaron pruebas automáticas utilizando `unittest`.

### 7. Conclusión

El desarrollo de EcoTech Solutions permitió aplicar conocimientos relacionados con el consumo de APIs externas, la autenticación y la seguridad de aplicaciones en Python.

La utilización de herramientas de inteligencia artificial fue útil para comprender errores y evaluar soluciones, pero también fue necesario probar el código y realizar correcciones para asegurar su funcionamiento.

Este proceso permitió mejorar la estabilidad del sistema y comprender la importancia de validar la información, controlar las excepciones y proteger los datos utilizados por una aplicación.