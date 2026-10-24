# KING CLEANER · aplicación web local

Versión inicial funcional, 23 de octubre de 2026. Python, Flask y MySQL. El código PyQt6 original y el SQL se conservan en `originales/`; no se ejecutó el `DROP DATABASE` ni se cargaron sus datos ilustrativos.

Para una instalación en otra PC desde cero, sigue **GUIA_01_INSTALACION_Y_PRUEBAS.md**. Para estudiar la arquitectura, las tecnologías y preparar la exposición, consulta **GUIA_02_DEFENSA_DEL_CODIGO.md**. Ambas guías están incluidas en el ZIP actualizado.

## Abrir en este equipo

1. Abre `Iniciar.cmd` mediante doble clic. Inicia los procesos en segundo plano y abre **http://127.0.0.1:5050**.
2. En el primer acceso, escribe tu nombre, un usuario y una contraseña propia de al menos 12 caracteres. No hay credenciales predeterminadas de la aplicación.
3. Comienza por **Almacén → Gestionar categorías → Gestionar materiales**. Crea únicamente registros reales.
4. Registra las recepciones de lotes con sus cantidades, fechas y ubicación.
5. Crea los productos terminados y registra una producción con los insumos efectivamente consumidos.
6. Registra ventas seleccionando los lotes terminados disponibles. Clientes es opcional; los precios se introducen por operación.
7. El recuadro **¡No olvides!** abre el calendario. Puedes crear, editar, completar o cancelar actividades.

Para detener la aplicación y cerrar MySQL de forma normal, abre `Detener.cmd`. Cerrar la pestaña del navegador no detiene los procesos. Los datos sobreviven al reinicio.

El puerto web es 5050 y el puerto de MySQL es 3307, ambos limitados a este equipo (`127.0.0.1`). No se instaló un servicio de Windows ni se configuró acceso público. MySQL puede administrarse también con Workbench si lo instalas posteriormente; Workbench no es necesario para usar la aplicación.

**Mantén juntas las carpetas `work` y `outputs` del espacio de trabajo.** Los accesos de este equipo usan el Python y los binarios de MySQL preparados en `work`, mediante rutas guardadas en `.local/runtime.json`. Si trasladas el proyecto a otro equipo, sigue la instalación manual de abajo.

## Qué funciona

| Módulo | Funciones |
|---|---|
| Inicio | Ventas/producción del día, lotes terminados con saldo, alertas, inventario reciente, últimas ventas y actividades. Cifras obtenidas de MySQL. |
| Almacén | Sectores a granel/por unidad, búsqueda por material/código/lote, filtros de estado, detalle, recepciones, ajuste con motivo e historial. |
| Catálogos | Consulta y alta de categorías, materiales, productos terminados y clientes. |
| Ventas | Diario/mensual/anual con fecha seleccionable, nueva venta con varias líneas, precios explícitos, detalle, descuento de lotes terminados y prevención de doble envío. |
| Producción | Registro de unidades terminadas y consumos manuales; descuento de insumos y generación del stock terminado dentro de una transacción. |
| Trazabilidad | Insumo → lote → orden → producto → venta registrada, consulta inversa desde un lote de insumo y filtros de texto/fecha. |
| Alertas | Lotes con saldo vencidos, incluidos los marcados VENCIDO; hasta 7 días críticos y hasta 30 días de atención. |
| Calendario | Mes anterior/siguiente/hoy, planificación al seleccionar un día, creación/consulta/edición, estados pendiente/completada/cancelada. |
| Reportes | Exportaciones CSV completas de inventario disponible, ventas y trazabilidad, compatibles con Excel. |
| Usuarios | Primer administrador local, acceso real con hash de contraseña, roles, alta administrada y cierre de sesión. |

Todos los roles pueden consultar los módulos. ADMIN tiene acceso completo. ALMACEN registra inventario, catálogos de materiales/productos y producción. VENTAS registra clientes y ventas. Cada usuario edita sus actividades; ADMIN también puede editar las de otros. Esta matriz es una decisión de implementación visible en Configuración, no una regla extraída del programa original.

## Reglas aplicadas y límites

- Selección **manual** de lotes. No se asumió una política FIFO/FEFO. La vista `v_inventario_peps` original sigue ordenando por vencimiento antes de ingreso.
- Un lote que vence **hoy** ya no puede consumirse, siguiendo el umbral del SQL original. El horario utilizado es Bolivia, UTC−04:00.
- Los insumos se descuentan al producir; las ventas descuentan productos terminados, nunca insumos directamente.
- No se inventan recetas, metas, estados de producción planificada, existencias históricas ni precios. El calendario es la herramienta de planificación.
- Las órdenes antiguas sin saldo terminado registrado se muestran como «Saldo no registrado». Las ventas históricas sin asignación de lote se muestran como «Sin asignación histórica».
- El modelo de ventas actual es de unidades envasadas. Venta de líquidos a granel, devoluciones, anulaciones, impuestos y facturación fiscal quedan fuera de esta versión.
- Los catálogos permiten consulta y alta. La modificación de catálogos existentes, el restablecimiento de contraseñas y la desactivación de usuarios no están incluidos en la interfaz.
- Los ajustes de insumos quedan auditados. No hay borrado de lotes, ventas u órdenes desde la interfaz, ni edición retroactiva de producción/ventas.
- Las alertas implementadas son de vencimiento. El campo de stock mínimo se conserva; aún no genera alertas adicionales.
- El calendario no envía correos ni avisos externos. Se registran actividades con hora; no hay modalidad separada de día completo.
- Los CSV son listados completos; no heredan filtros de otras pantallas. La exportación de inventario conserva el criterio de la vista original, que incluye estado DISPONIBLE y saldo positivo; revisa Alertas para los vencimientos.
- No se implementaron gráficos estadísticos, conforme a su prioridad secundaria. No se afirma certificación ni cumplimiento SENASAG.
- La interfaz se adapta a anchos menores; tablas y calendario usan desplazamiento horizontal cuando hace falta.

## Archivos y conservación

| Archivo/carpeta | Uso |
|---|---|
| `app.py` | Rutas, acceso, formularios, consultas y exportaciones. |
| `services.py` | Recepciones, ajustes, producción y ventas transaccionales. |
| `db.py` | Conexiones parametrizadas y transacciones. |
| `schema.py` | Inicialización sin borrado ni ejemplos y extensiones incrementales. |
| `manage.py` | Inicialización, migración y copia lógica de la base. |
| `templates/`, `static/` | Interfaz web y comportamiento del navegador. |
| `tests/` | Pruebas contra MySQL real, en una base separada. |
| `originales/` | Código, SQL y capturas originales de referencia. |
| `.env` | Conexión local y clave de sesión; privado, no incluido en el ZIP. |
| `.local/mysql-data/` | Datos persistentes de este MySQL local. No eliminar. |
| `.local/mysql-admin.json` | Credencial administrativa generada localmente. No compartir. |
| `.local/runtime.json` | Rutas del entorno instalado en este equipo. |

La cuenta utilizada por la web tiene permisos de SELECT/INSERT/UPDATE/DELETE sobre la base del negocio, sin permisos de creación o eliminación de tablas. La contraseña de MySQL es independiente de la contraseña del usuario de la aplicación.

No compartas `.env`, `.local`, copias de la base ni archivos de registros si contienen datos del negocio. El ZIP de entrega excluye estos archivos y los entornos de ejecución.

## Instalación manual en otro equipo

Requiere Python 3.12 o compatible y MySQL Server 8.4. MySQL para Windows está disponible en el [sitio oficial](https://dev.mysql.com/downloads/mysql/8.4.html?os=3); se utilizó la distribución ZIP oficial 8.4.13. Los binarios no están incluidos en el ZIP del proyecto.

En la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` localmente con la conexión a tu servidor. Para la instalación o migración usa temporalmente una cuenta con los permisos DDL necesarios; después configura una cuenta de aplicación con los permisos mínimos indicados arriba. No pegues las contraseñas en chats o capturas.

**Base nueva vacía:** ejecuta `python manage.py init` con el entorno virtual. Se crea la base si no existe y se rechaza continuar si ya contiene objetos. Solo se extraen del SQL original las declaraciones de tablas y vistas, sin DROP ni INSERT.

**Base existente:** no ejecutes el SQL original. Revisa primero su compatibilidad. Con el servidor sin escrituras concurrentes y una cuenta administrativa configurada, ejecuta `python manage.py migrate`. Guarda una copia lógica en `.local/backups` antes de añadir tablas `kc_*`. Conserva las tablas y vistas originales. Prueba antes sobre una copia de tu base: la inicialización DDL de MySQL no es atómica y una interrupción puede dejar objetos parcialmente creados.

Después de configurar la cuenta de aplicación:

```powershell
.\.venv\Scripts\python.exe app.py
```

Abre http://127.0.0.1:5050. El servidor se limita a localhost y no activa depuración. Los accesos `Iniciar.cmd`/`Detener.cmd` corresponden al entorno preparado aquí; en otro equipo configura su `runtime.json` o usa el comando anterior con tu servidor MySQL habitual.

## Copias de seguridad

Con la configuración de conexión adecuada, `python manage.py backup` genera una copia SQL de tablas, registros y vistas en `.local/backups`. Haz la copia sin migraciones ni cambios DDL concurrentes. Conserva también código y configuración en un lugar privado. La restauración debe hacerse primero en una base vacía de prueba y verificarse antes de reemplazar una base real. Esta entrega prueba conservación mediante migraciones, pero no certifica una restauración de datos comerciales reales.

## Pruebas

Instala pytest en el entorno de desarrollo. Define `KC_TEST_ADMIN_FILE` con la ruta a un JSON privado con `user`, `password` y `port` de un administrador local de pruebas. Ejecuta:

```powershell
python -m pytest tests -q
```

Cada ejecución crea una base `king_cleaner_test_<identificador>` separada; sus datos se identifican como TEST. Se mantiene para auditoría, nunca se usa la base del negocio. Las pruebas no deben ejecutarse con credenciales de un servidor de producción. Consulta `VERIFICACION.md` para los resultados de esta entrega.

## Mapa de adaptación

`MainSystemWindow` → `base.html` y rutas; `HomeDashboardView` → inicio; `InventoryView` → inventario/detalle; `SalesView` → ventas reales y detalle; `VistaTrazabilidadSENASAG` → trazabilidad; `LoginWindow`/`RegisterWindow` → acceso real, primer administrador y alta administrada. Los componentes de tarjetas y logo se adaptaron a HTML/CSS. `BDconexion.py` no estaba disponible: `db.py` y `services.py` reemplazan esa dependencia sin alterar los originales.

Las nueve tablas originales y tres vistas se conservan. Las extensiones son `kc_users`, `kc_events`, `kc_movimientos`, `kc_stock_terminado`, `kc_asignaciones_venta`, `kc_requests` y `kc_migrations`. No se rellenan relaciones históricas por deducción.
