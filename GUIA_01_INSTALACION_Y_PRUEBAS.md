# KING CLEANER — instalación en otra PC y pruebas

Guía paso a paso para Windows · Revisada el 23 de octubre de 2026

## 1. Qué vas a conseguir

Al terminar tendrás la aplicación abierta en el navegador de la nueva PC, con Python atendiendo las pantallas y MySQL guardando los datos. La dirección será **http://127.0.0.1:5050**. No necesitas publicar un sitio ni contratar alojamiento.

Esta guía instala una **base nueva vacía**. Descargar el ZIP del código no traslada los registros ni usuarios de la PC anterior. Si necesitas trasladar datos existentes, consulta el apartado 15 antes de inicializar la base.

Los ejemplos asumen Windows 11 de 64 bits. Necesitas permiso para instalar programas y configurar el servicio de MySQL. Internet se usa para descargar instaladores y dependencias; una vez preparado el equipo, la operación habitual funciona sin conexión a internet.

## 2. Qué instalar y qué no hace falta

| Elemento | ¿Es necesario? | Para qué sirve |
|---|---|---|
| Python 3.12 de 64 bits | Sí | Ejecuta el servidor y la lógica del proyecto. El entorno original usó 3.12.14. |
| MySQL Community Server 8.4 | Sí | Guarda usuarios, inventario, ventas, producción y actividades. |
| Edge, Chrome o Firefox | Sí, uno de ellos | Muestra y permite usar la aplicación. |
| Bibliotecas de `requirements.txt` | Sí | Se instalan con un comando; no se descargan individualmente. |
| MySQL Workbench | Opcional | Permite inspeccionar tablas y ejecutar consultas gráficamente. No sustituye a MySQL Server. |
| Visual Studio Code | Opcional, útil para estudiar | Permite abrir y editar el proyecto. No es necesario para usarlo. |
| pytest | Solo para pruebas automatizadas | Ejecuta la batería de pruebas de integración. |
| PyQt6 | No para la web | Pertenece a la aplicación de escritorio original. |
| Node.js, npm, XAMPP, PHP, Docker | No para esta entrega | La aplicación no depende de estas herramientas. |
| Codex o una cuenta de OpenAI | No para ejecutar | Se utilizó asistencia de Codex durante el desarrollo, no como dependencia del sitio. |

## 3. Descargar y extraer el ZIP

1. Descarga **`KING_CLEANER_web_codigo.zip`** desde el enlace de entrega del chat y llévalo a la nueva PC, mediante descarga o memoria USB.
2. En el Explorador de Windows, pulsa con el botón derecho sobre el ZIP y elige **Extraer todo**.
3. Extrae en una carpeta que puedas modificar, por ejemplo Documentos. Dentro encontrarás `king-cleaner-web`.
4. Abre esa carpeta. Debes ver `app.py`, `requirements.txt`, `manage.py`, `schema.py`, `templates`, `static` y `originales`.
5. No ejecutes los archivos desde dentro del ZIP. No hace falta copiar la carpeta `work` de la PC anterior para esta instalación manual.

El ZIP no incluye Python, los binarios de MySQL, `.env`, las contraseñas, el entorno virtual ni los datos locales. Esto es intencional: cada PC debe tener su propia configuración.

**Importante:** `Iniciar.cmd` y `Detener.cmd` son accesos del entorno preparado en la PC original. Dependen de `.local/runtime.json`, que no se comparte. En la nueva PC utiliza el arranque descrito en esta guía. No copies ese JSON esperando que sus rutas existan en otro equipo.

## 4. Instalar Python

Descarga el **Python Install Manager** desde [python.org](https://www.python.org/downloads/), instálalo y abre una terminal nueva. Este administrador permite instalar una versión concreta de Python. [Documentación oficial de Windows](https://docs.python.org/3/using/windows.html).

En PowerShell:

```powershell
py install 3.12
py -3.12 --version
```

El segundo comando debe mostrar `Python 3.12.x`. No hace falta que el último número coincida exactamente con la PC original. Esta guía conserva la serie 3.12 para reducir diferencias con el entorno probado.

Si ya tienes Python 3.12 y `py -3.12 --version` funciona, omite la instalación. Si `py install` no se reconoce pero `py -3.12` funciona, probablemente tienes el lanzador anterior: puedes continuar. Si no tienes 3.12, instala el administrador oficial; no descargues una versión desde páginas no oficiales para resolverlo.

## 5. Instalar MySQL Server

Abre la [descarga oficial de MySQL Community Server 8.4](https://dev.mysql.com/downloads/mysql/8.4.html?os=3). Selecciona Windows de 64 bits y el paquete MSI. Para la serie 8.4 se utiliza el MSI del servidor y **MySQL Configurator**, no es necesario buscar el antiguo instalador conjunto de la serie 8.0. [Instalación oficial para Windows](https://dev.mysql.com/doc/refman/8.4/en/windows-installation.html).

Durante la instalación y configuración:

1. Instala MySQL Server y abre el configurador cuando se ofrezca.
2. Para una PC de desarrollo, elige la configuración de equipo de desarrollo si aparece.
3. Mantén TCP/IP y anota el puerto. Esta guía usa **3306**; si está ocupado, elige otro y úsalo de forma consistente.
4. No habilites una excepción de firewall para acceso desde otros equipos: este proyecto se usará localmente.
5. Define una contraseña propia para el administrador MySQL **root** y guárdala de forma privada.
6. Configura MySQL como servicio de Windows, preferiblemente con inicio automático, y anota el nombre que se muestra.
7. Aplica los cambios y confirma que la configuración finalizó correctamente.

Los nombres exactos de las pantallas pueden variar. El [manual de MySQL Configurator](https://dev.mysql.com/doc/refman/8.4/en/mysql-configurator.html) describe ese asistente.

Comprueba que el servicio está activo: pulsa `Win + R`, escribe `services.msc`, busca el servicio MySQL y verifica que diga **En ejecución**. No presupongas que se llama MySQL80: utiliza el nombre instalado en tu equipo.

### Tres contraseñas diferentes

| Credencial | Dónde se utiliza |
|---|---|
| `root` de MySQL | Instalación, creación de cuentas y administración de la base. |
| `king_cleaner` de MySQL | Conexión de la aplicación a su base. Se guarda en `.env`. |
| Usuario administrador de KING CLEANER | Acceso a la página desde el navegador. Se crea en el primer acceso. |

No son la misma cuenta. No uses la contraseña de root como contraseña de todos los usuarios.

## 6. Abrir una terminal en la carpeta correcta

En el Explorador, entra en la carpeta `king-cleaner-web`. Escribe `powershell` en la barra de direcciones y pulsa Enter. La terminal se abrirá en esa carpeta.

Comprueba la ubicación:

```powershell
Get-Location
Get-ChildItem app.py, requirements.txt, manage.py
```

Si algún archivo no aparece, estás en otra carpeta. Entra en la carpeta que contiene esos tres archivos antes de continuar. No copies el texto `PS C:\...>` que aparece al principio de la terminal: no forma parte de los comandos.

## 7. Crear el entorno e instalar bibliotecas

Ejecuta, uno por uno:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Espera a que termine cada comando. El último debe indicar que no hay requisitos incompatibles.

El entorno `.venv` contiene las bibliotecas de este proyecto. Usar su `python.exe` explícitamente evita depender de qué Python está seleccionado globalmente y evita tener que activar scripts de PowerShell.

No copies `.venv` desde otra PC: se crea de nuevo. Tampoco necesitas instalar Flask o PyMySQL manualmente uno por uno; están declarados en `requirements.txt`.

## 8. Crear la configuración y la base vacía

### 8.1 Preparar `.env`

Solo si `.env` todavía no existe:

```powershell
Copy-Item .env.example .env
notepad .env
```

Para la inicialización, configura temporalmente root. Sustituye el texto de ejemplo por tu contraseña real **solo en tu PC**:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=control_produccion_db
DB_USER=root
DB_PASSWORD='ESCRIBE_AQUI_TU_CLAVE_ROOT'
SECRET_KEY=
APP_PORT=5050
```

Si elegiste otro puerto en MySQL, cambia `DB_PORT`. Las comillas delimitan el valor; no forman parte de la contraseña. Si tu contraseña contiene comillas o barras invertidas, respeta el formato de cadenas de dotenv; evita introducir espacios adicionales por accidente.

Puedes dejar `SECRET_KEY` vacío: la aplicación genera una clave privada de sesión en `.local/session.key`. Esa clave no es una contraseña para iniciar sesión.

Guarda el archivo como **`.env`**, sin `.txt`. En el Explorador activa la visualización de extensiones si no puedes comprobarlo. No sobrescribas un `.env` ya configurado sin revisar su contenido.

### 8.2 Inicializar una sola vez

```powershell
.\.venv\Scripts\python.exe manage.py init
```

Resultado esperado:

```text
Base nueva inicializada sin registros de ejemplo.
```

Este proceso crea la base si no existe y sus tablas/vistas. Rechaza continuar si la base ya tiene objetos. `init` no se repite cada vez que abras la página.

**No abras y ejecutes directamente `originales/Base de datos proyecto.sql`: empieza con un borrado de base.** El programa extrae únicamente las declaraciones necesarias del esquema y omite el borrado y los registros ilustrativos.

Si `init` informa que la base contiene objetos, detente y comprueba si es una instalación ya existente. No borres tablas para hacer desaparecer el mensaje.

## 9. Crear la cuenta MySQL de la aplicación

La página debe funcionar con una cuenta propia, sin permisos administrativos.

### 9.1 Entrar a MySQL

Desde PowerShell, si usaste la ruta estándar del MSI:

```powershell
& 'C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe' -h 127.0.0.1 -P 3306 -u root -p
```

Corrige la ruta si instalaste en otra carpeta y el puerto si lo cambiaste. La contraseña se solicita después; no la escribas al lado de `-p`.

También puedes ejecutar las consultas del siguiente apartado desde una conexión administrativa de MySQL Workbench. Es opcional y se descarga desde [MySQL Workbench](https://dev.mysql.com/downloads/workbench/).

### 9.2 Crear usuario y permisos

Cuando veas el indicador `mysql>`, ejecuta estas sentencias SQL. Cambia el marcador de contraseña por una clave nueva propia; no uses literalmente la frase de ejemplo.

```sql
CREATE USER 'king_cleaner'@'localhost'
IDENTIFIED BY 'REEMPLAZAR_POR_UNA_CLAVE_PROPIA';

GRANT SELECT, INSERT, UPDATE, DELETE, SHOW VIEW
ON control_produccion_db.*
TO 'king_cleaner'@'localhost';

SHOW GRANTS FOR 'king_cleaner'@'localhost';
EXIT;
```

Si el usuario ya existe, no lo elimines ni cambies su clave automáticamente; comprueba si corresponde a esta instalación. `SHOW VIEW` permite incluir las vistas en las copias lógicas. La cuenta web no necesita permisos para crear o eliminar tablas.

### 9.3 Cambiar `.env` a la cuenta de la aplicación

Vuelve a abrir `.env` y cambia únicamente usuario y contraseña:

```dotenv
DB_USER=king_cleaner
DB_PASSWORD='LA_CLAVE_QUE_ACABAS_DE_CREAR'
```

Mantén host, puerto, nombre de base y puerto web. Guarda y cierra. La contraseña root ya no debe quedar en el `.env` de uso diario.

## 10. Arrancar la página y crear el administrador

En PowerShell, desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe app.py
```

Resultado esperado:

```text
KING CLEANER · http://127.0.0.1:5050
```

La terminal queda ocupada: **es normal**, el servidor está trabajando. Déjala abierta y entra en **http://127.0.0.1:5050** desde el navegador de esa misma PC. Puedes comprobar también **http://127.0.0.1:5050/health**; debería responder `{"status":"ok"}`.

En el primer acceso:

1. Escribe tu nombre completo.
2. Elige el nombre de usuario de KING CLEANER.
3. Define y confirma una contraseña de al menos 12 caracteres.
4. Pulsa **Crear administrador**.
5. Inicia sesión con esa cuenta, no con root de MySQL.

El tablero empieza sin operaciones. Ver ceros después de una consulta correcta es esperable en una instalación nueva.

`127.0.0.1` significa «este equipo». Ese enlace abierto en otro ordenador apunta a ese otro ordenador, no a tu servidor. Esta entrega no está configurada para acceso por red local o internet.

## 11. Apagar y volver a abrir

Para detener la página en esta instalación manual, vuelve a la terminal y pulsa **Ctrl + C**. Cerrar solamente la pestaña del navegador no detiene Python. El servicio MySQL puede seguir funcionando; no es necesario detenerlo cada vez.

Para abrir al día siguiente:

1. Comprueba que el servicio MySQL esté en ejecución.
2. Abre PowerShell en `king-cleaner-web`.
3. Ejecuta `.\.venv\Scripts\python.exe app.py`.
4. Abre la dirección local e inicia sesión.

No repitas `init`, no reinstales dependencias y no vuelvas a crear el administrador.

Opcionalmente puedes guardar un archivo nuevo llamado `Abrir_en_esta_PC.cmd` dentro del proyecto, con este contenido:

```bat
@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" app.py
pause
```

Ese acceso mantiene la terminal visible y funciona con el entorno virtual de la carpeta actual. MySQL debe estar iniciado. Abre el navegador por separado. No modifica los accesos originales.

## 12. Prueba manual de extremo a extremo

### Preparar un entorno de práctica

Los datos siguientes son **ejemplos sintéticos de software**, no existencias reales ni una receta química. Úsalos únicamente en una base de práctica.

Para aislarla sin alterar tu instalación diaria, extrae otra copia del ZIP en una carpeta distinta, por ejemplo `king-cleaner-practica`. Repite los pasos de entorno/configuración/inicialización, pero usa:

- `DB_NAME=king_cleaner_practica`.
- `APP_PORT=5051`.
- Durante `init`, root solo para inicializar.
- Después, la cuenta `king_cleaner`, añadiendo como root `GRANT SELECT, INSERT, UPDATE, DELETE, SHOW VIEW ON king_cleaner_practica.* TO 'king_cleaner'@'localhost';`.

Abre **http://127.0.0.1:5051** y crea un administrador propio de práctica. No copies `.env` ni `.local` de la instalación real sobre esta copia. No se cambia el puerto de MySQL: ambas bases pueden usar el mismo servidor local.

### Recorrido con resultados esperados

| Paso | Acción en la interfaz | Resultado esperado |
|---|---|---|
| 1 | Almacén → Gestionar categorías. Añadir `PRUEBA Líquidos`, sector GRANEL. | Categoría visible en el listado. |
| 2 | Gestionar materiales. Código `PRUEBA-MP-01`, nombre `Material de práctica`, categoría anterior, LITROS, mínimo 0. | Material disponible en recepción. |
| 3 | Recibir lote `PRUEBA-INS-01`, cantidad 100, ingreso hoy, vencimiento dentro de 5 días, tanque `Práctica A`. | Saldo 100 L; movimiento de recepción; alerta crítica por vencimiento próximo. |
| 4 | Productos terminados. Código `PRUEBA-PT-01`, nombre `Producto de práctica`, volumen 1 litro. | Producto disponible para producción. |
| 5 | Registrar producción. Lote `PRUEBA-FINAL-01`, 10 unidades. Seleccionar el lote de insumo y consumir 10 L. | Insumo 90 L; terminado 10 unidades; trazabilidad creada. |
| 6 | Clientes. Añadir `Cliente de práctica`, sin inventar identificación personal. | Cliente disponible en venta. |
| 7 | Nueva venta. Cliente de práctica, lote final anterior, cantidad 2, precio 12.50. | Venta Bs. 25,00; stock terminado 8; insumo continúa en 90 L. |
| 8 | Abrir la venta y luego Trazabilidad, seleccionando el lote final. | Se ve el consumo de insumo y la venta vinculada al cliente. |
| 9 | Intentar vender 9 unidades del lote que tiene 8. | Mensaje de stock insuficiente; no se crea otra venta ni cambia el saldo. |
| 10 | Abrir el lote de insumo y ajustar su saldo a 89 con motivo `Conteo físico de práctica`. | Saldo 89 L y movimiento de −1 L con autor y motivo. |
| 11 | Inicio → ¡No olvides! → Abrir cronograma. Crear `Actividad de práctica`, con inicio y fin válidos. | Aparece en el día seleccionado y permanece al recargar. |
| 12 | Editar la actividad y marcarla completada. | Cambia de estado y conserva el registro. |
| 13 | Exportar ventas desde Reportes. | CSV con una venta por importe equivalente a Bs. 25,00, si no añadiste otras; el valor numérico del archivo puede verse como `25.00`. |
| 14 | Cerrar sesión, intentar abrir Inventario y volver a entrar. | Solicita acceso; permite volver con las credenciales válidas. |
| 15 | Detener Python con Ctrl+C y volver a arrancarlo. | Se mantienen la venta, los saldos y la actividad. |

No uses los números del ejemplo como criterio para datos reales. Después de vender, vuelve al listado de Producción para comprobar el stock terminado; no busques ese saldo en el inventario de insumos.

### Pruebas adicionales

- Crea una categoría UNIDADES, un material con unidad UNIDADES y un lote. Intenta ingresar una cantidad fraccionaria: debe rechazarse.
- Intenta repetir el mismo número de lote para el mismo material: debe rechazarse.
- Recibe un lote de práctica con vencimiento hoy: debe aparecer vencido y no estar disponible para producción.
- Crea usuarios ALMACEN y VENTAS desde Configuración. Verifica que VENTAS no puede recibir lotes y ALMACEN no puede registrar ventas.
- Prueba los filtros Diario/Mensual/Anual con una fecha que incluya la venta y otra que no la incluya.

## 13. Ejecutar las pruebas automatizadas

Esta parte requiere MySQL activo y una cuenta administrativa **del servidor local de pruebas**. La batería crea una base aleatoria separada y limpia sus propias tablas entre casos. No uses un servidor de producción.

Desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
New-Item -ItemType Directory -Force .local
notepad .local\test-admin.json
```

Guarda este JSON cambiando la clave y, si corresponde, el puerto:

```json
{
  "user": "root",
  "password": "ESCRIBE_AQUI_TU_CLAVE_ROOT_LOCAL",
  "port": 3306
}
```

Es un archivo privado local. En JSON una barra invertida se escribe `\\` y una comilla interna se escribe `\"`. No lo incluyas en el ZIP ni en capturas. No uses comas después del último campo.

Luego:

```powershell
$env:KC_TEST_ADMIN_FILE = (Resolve-Path '.local\test-admin.json').Path
.\.venv\Scripts\python.exe -m pytest tests -q
```

Resultado esperado para esta versión: **`18 passed`**. La duración cambia según el equipo. Si aparece `skipped`, las pruebas se omitieron: eso **no** equivale a que aprobaron; revisa `KC_TEST_ADMIN_FILE`.

Para ver los nombres y más detalles:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

Se prueban transacciones, stock insuficiente, ventas concurrentes, reenvíos, fechas, decimales, autenticación, permisos, calendario, migración y CSV. No se automatiza la instalación gráfica de Windows ni se certifica seguridad total.

Cada ejecución deja una base `king_cleaner_test_<identificador>` para revisión. No utiliza la base comercial. El archivo `VERIFICACION.md` describe la ejecución realizada durante el desarrollo; tú debes registrar también el resultado obtenido en la nueva PC.

## 14. Solución de problemas

| Síntoma | Qué comprobar |
|---|---|
| `py` no se reconoce | Instala Python y abre una terminal nueva; verifica `py -3.12 --version`. |
| No encuentra `requirements.txt` o `app.py` | Abre PowerShell en la carpeta extraída correcta. |
| Error al activar scripts de PowerShell | No hace falta activar: usa `.\.venv\Scripts\python.exe` como en esta guía. |
| `ModuleNotFoundError: flask` | Instalaste en otro Python; vuelve a ejecutar pip con el ejecutable de `.venv`. |
| No puede descargar paquetes | Comprueba internet, proxy y acceso a PyPI; no omitas dependencias. |
| `Access denied for user` | Verifica usuario, contraseña, host y permisos. No confundas usuario web con usuario MySQL. |
| `Can't connect` / error 2003 | Comprueba el servicio MySQL y `DB_PORT`. 3306 es la propuesta para la PC nueva; 3307 se usó en el entorno original. |
| `Unknown database` | Revisa `DB_NAME` y si ejecutaste `manage.py init` con éxito. |
| `Table ... doesn't exist` | Puede faltar la inicialización o haber quedado incompleta; revisa la salida de `init`, no ejecutes el SQL destructivo. |
| «La base contiene objetos» | Ya existe un esquema. Comprueba cuál es; no repitas una instalación nueva sobre datos existentes. |
| Falta `.local/runtime.json` | Ejecutaste los accesos de la PC original. Usa el comando manual de esta guía. |
| El navegador no conecta | Mantén Python abierto y revisa que hayas escrito `http://`, puerto 5050. |
| Puerto 5050 ocupado | Detén una ejecución anterior de este mismo proyecto o cambia `APP_PORT`, por ejemplo a 5052, y abre ese puerto. No cierres procesos desconocidos. |
| Cambiaste `.env` pero nada cambia | Detén y reinicia Python. Variables `DB_*` definidas previamente en la terminal pueden prevalecer; prueba una terminal nueva. |
| No aparece un material al recibir | Debes darlo de alta en Materiales; antes necesitas su categoría. |
| No hay lotes para vender | Debes registrar productos terminados y producción con consumos. Recibir insumos no crea stock terminado. |
| Error 400 de formulario | Recarga el formulario e inicia sesión si venció. Revisa campos y fechas. |
| Error 403 | El rol no tiene permiso; solicita al administrador que realice la operación adecuada. |
| Olvidaste la contraseña web | Esta versión no tiene recuperación de contraseña en pantalla; requiere soporte administrativo. No reinicialices la base. |

## 15. Copias, traslado de datos y entrega

Para una copia lógica de la base configurada:

```powershell
.\.venv\Scripts\python.exe manage.py backup
```

Se guarda un SQL en `.local/backups`. La cuenta necesita SELECT y SHOW VIEW. Haz la copia sin cambios de estructura concurrentes. Los respaldos contienen información real y deben guardarse de forma privada.

Trasladar datos existentes es distinto de instalar vacío: requiere una copia de la base de origen, una base de destino vacía, revisión de los `DEFINER` de las vistas y sus permisos, importación y comprobación de conteos/relaciones antes de usarla. No ejecutes `init` sobre una base ya restaurada ni importes un respaldo sobre datos que quieras conservar. No copies la carpeta interna de datos de MySQL entre servidores en ejecución. Esta guía no presenta una restauración como si ya estuviera validada en tu nueva PC.

Para entregar **solo código**, comparte el ZIP. Para trabajar a diario, conserva de forma privada el proyecto, `.env` y copias verificadas de MySQL. Tener el código no sustituye un respaldo de la base.

## 16. Lista final de comprobación

- [ ] ZIP extraído y archivos del proyecto visibles.
- [ ] Python 3.12 y MySQL Server instalados.
- [ ] Entorno virtual creado y `pip check` correcto.
- [ ] `.env` guardado sin extensión `.txt`.
- [ ] Base nueva inicializada una sola vez.
- [ ] Cuenta MySQL de la web sin permisos administrativos.
- [ ] `/health` responde y el navegador abre la aplicación.
- [ ] Administrador web propio creado.
- [ ] Prueba manual realizada en una base separada.
- [ ] `18 passed` obtenido en esta PC, o fallos anotados y resueltos.
- [ ] Reinicio de Python conserva registros.
- [ ] Se conoce cómo iniciar, detener y respaldar.

Conserva una pequeña ficha de instalación: fecha, versión de Python, versión/puerto de MySQL, carpeta del proyecto, resultado de pruebas y observaciones. **No incluyas contraseñas en esa ficha.**

### Comprobación realizada al preparar esta guía

Se extrajo el ZIP en una carpeta nueva de la PC de desarrollo, se creó otro entorno virtual, se instalaron las dependencias y `pip check` no encontró incompatibilidades. Se inicializó una base separada vacía, se conectó con una cuenta de permisos limitados y se comprobaron `/health`, el primer acceso y una copia lógica. Esto verifica la parte del paquete y la configuración; no equivale a haber ejecutado los instaladores gráficos o las pruebas en la otra PC. Las 18 pruebas son las de la entrega funcional previa y deben repetirse en el equipo de destino.
