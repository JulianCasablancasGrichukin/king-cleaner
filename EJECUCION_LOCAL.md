# Ejecución y despliegue local

Preparado y verificado el 24 de octubre de 2026 en este equipo.

## Abrir, iniciar y detener

La aplicación está en http://127.0.0.1:5050. En el primer acceso se crea el
administrador con una contraseña propia de al menos 12 caracteres.

Para volver a iniciar, abre `Iniciar.cmd` o ejecuta desde esta carpeta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iniciar.ps1 -NoBrowser
```

Para detener ambos servidores conservando los datos, abre `Detener.cmd`.
Cerrar el navegador no detiene los servidores. No se configuró inicio automático
con Windows.

## Preparación realizada

1. Se utilizó Python 3.11.4 instalado en
   `C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe`.
2. Se creó un entorno virtual independiente y se instalaron las versiones fijadas
   por el proyecto, más pytest para la verificación:

   ```powershell
   & 'C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe' -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt pytest
   ```

3. Se utilizaron los binarios existentes de MySQL Community Server 8.0.39 en
   `C:\Program Files\MySQL\MySQL Server 8.0\bin`. Se inicializó una instancia
   independiente en `.local/mysql-data`, limitada a `127.0.0.1:3307`, con zona
   horaria `-04:00`. No se modificaron otras bases o servicios MySQL.
4. El script privado `.local/setup_local.py` creó la base
   `control_produccion_db` mediante las funciones de `schema.py`, sin datos de
   ejemplo. Este script es de un solo uso: no debe repetirse para iniciar.
   Se asignó una contraseña aleatoria a root y se creó una cuenta `king_cleaner`
   con SELECT, INSERT, UPDATE y DELETE únicamente sobre la base del negocio.
5. Se generaron `.env`, `.local/mysql-admin.json` y `.local/runtime.json`.
   Guardan la conexión, credenciales y rutas de este equipo. No compartirlos.
6. Se ejecutó `Iniciar.ps1 -NoBrowser`. Inicia MySQL y ejecuta `app.py` en
   segundo plano. `app.py` sirve Flask mediante Waitress con cuatro hilos,
   sin depuración, en `127.0.0.1:5050`.

El recorrido de una petición es: navegador → Waitress → Flask → PyMySQL → MySQL.
Flask renderiza las plantillas de `templates/`; los estilos y JavaScript están en
`static/`. Los datos persisten en `.local/mysql-data`.

## Verificación realizada

- `GET /health`: HTTP 200 y `{"status":"ok"}`; consulta la migración en MySQL.
- Acceso a `/`: HTTP 200 tras las redirecciones y formulario de administrador inicial.
- `python -m pip check`: ninguna dependencia incompatible.
- Pruebas de integración: **18 aprobadas**, contra MySQL real en una base
  separada `king_cleaner_test_*`, conservada para auditoría. No se introdujeron
  registros de prueba en la base del negocio.

Para repetir las pruebas desde PowerShell:

```powershell
$env:KC_TEST_ADMIN_FILE = Join-Path (Get-Location).Path '.local\mysql-admin.json'
.\.venv\Scripts\python.exe -m pytest tests -q
```

Los registros de los servidores están en `.local/app-out.log`,
`.local/app-err.log`, `.local/mysql-out.log` y `.local/mysql-err.log`.

## Alcance del despliegue

Se realizó un despliegue local en este equipo. No se publicó en Internet, no se
configuró dominio ni HTTPS y no se creó un servicio de Windows. La configuración
actual solo admite acceso desde este equipo. Las rutas de `runtime.json` son
específicas de esta instalación.

Para publicar en un servidor se necesitarían un destino de alojamiento, MySQL
persistente, configuración privada de credenciales y un servicio que mantenga
Waitress ejecutándose detrás de un proxy con HTTPS. Esa publicación no forma
parte de lo ejecutado aquí.
