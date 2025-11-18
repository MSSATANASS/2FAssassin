# Documentación de funciones clave

Esta referencia resume los componentes que se exponen al ejecutar `assassin.py` y enlaza con documentación externa
útil para las funciones presentadas por la herramienta.

## `build_parser`

Crea el analizador de argumentos que alimenta al CLI. Define todas las banderas documentadas en el README (`--scan`,
`--check`, `--mode`, etc.) y actúa como una única fuente de la interfaz soportada.

## `safe_import`

Carga módulos de apoyo bajo demanda y conserva el resultado en `_IMPORT_CACHE` para evitar inicializaciones repetidas.
Además, asegura que un error al cargar una dependencia termine el proceso con un mensaje claro en lugar de provocar
trazas de pila inesperadas.

## `scan` y `advanced`

Estas funciones coordinan los escaneos básicos y avanzados, respectivamente. Ambas validan que `msfrpc` esté
instalado antes de abrir una consola en Metasploit y ejecutar los comandos `db_nmap` necesarios para enumerar hosts y
servicios. La variante "advanced" ejecuta un conjunto más amplio de comandos y muestra el resultado de manera
interactiva.

## `run_actions`

Encapsula la lógica de control de flujo del CLI. Evalúa los argumentos recibidos y despacha la ejecución hacia las
rutinas correspondientes (escaneo, ataques de Heartbleed, módulos SSH, etc.). También coordina módulos secundarios
como `post.prepare`, `post.pka` y `check.vuln.pub.stat` utilizando `safe_import` para diferir las dependencias hasta que
sean necesarias.

## Documentación externa para flujos de transacciones

En caso de que las funciones anteriores se integren con flujos que deban enviar o firmar transacciones (por ejemplo,
cuando una fase post-explotación necesite interactuar con un intercambio o billetera), la referencia oficial del SDK
de Coinbase Developer Platform describe el uso de su cliente Python, los parámetros requeridos y las opciones de
seguimiento de estado. Consulta "Sending transactions" en la documentación oficial para obtener ejemplos actualizados
y consideraciones de seguridad: <https://coinbase.github.io/cdp-sdk/python/#sending-transactions>.
