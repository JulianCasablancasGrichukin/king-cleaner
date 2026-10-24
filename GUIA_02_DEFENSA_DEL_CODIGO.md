# KING CLEANER — guía para comprender y defender el código

Basada en la implementación entregada · 23 de octubre de 2026

## 1. Qué debes poder explicar primero

El proyecto es una aplicación web local para controlar insumos, lotes, producción, ventas, trazabilidad y actividades. Se abre en un navegador, pero el procesamiento ocurre en Python y los datos se guardan en MySQL.

No es una página estática: al registrar una venta se validan cantidades, se guardan cabecera y detalles, se vincula el lote terminado y se actualiza su saldo. Tampoco es una aplicación PyQt6 ejecutándose dentro del navegador: la interfaz de escritorio se adaptó a tecnologías web.

Una presentación breve que puedes adaptar:

> KING CLEANER organiza la operación de un negocio de productos de limpieza. Partimos de una interfaz de escritorio en PyQt6 y de un esquema MySQL. Conservamos el modelo original y adaptamos la interfaz a una aplicación web local con Python y Flask. Priorizamos inventario, ventas y trazabilidad con datos reales, además de alertas y un calendario persistente. Las operaciones de producción y venta usan transacciones para evitar registros incompletos y saldos negativos por concurrencia.

Comprende cada afirmación antes de utilizarla. Si te preguntan algo que no está implementado, explica el límite; no lo presentes como una función terminada.

## 2. Tecnologías y herramientas: qué hizo cada una

| Tecnología/herramienta | Papel real en el proyecto | Dónde lo compruebas |
|---|---|---|
| Python 3.12 | Lenguaje del servidor, validaciones, operaciones y administración. | Archivos `.py`; entorno usado 3.12.14. |
| Flask 3.1.3 | Define rutas web, recibe formularios, gestiona respuestas y sesiones. | Importaciones y decoradores de `app.py`. |
| Jinja2 | Genera HTML con datos del servidor y reutiliza plantillas. Llega como dependencia de Flask. | `templates/`, `extends`, `block`, bucles y variables. |
| HTML | Estructura de páginas, formularios, enlaces y tablas. | Plantillas `.html`. |
| CSS | Diseño, colores, tarjetas, panel lateral y adaptación de tamaño. | `static/style.css`. |
| JavaScript | Interacciones pequeñas: añadir/quitar líneas, desactivar el botón al enviar y volver. | `static/app.js`. |
| MySQL Server 8.4 | Motor de base de datos relacional. Se probó con 8.4.13. | Tablas/vistas y conexiones. |
| InnoDB | Motor de las tablas; permite transacciones y bloqueos de filas. | SQL original y comportamiento de las operaciones. |
| SQL | Lenguaje de consultas y cambios en la base. | `app.py`, `services.py`, `schema.py`, `manage.py`. |
| PyMySQL 1.2.3 | Controlador que permite a Python conectarse a MySQL. | `db.py`, `pymysql.connect`, cursores. |
| python-dotenv 1.2.4 | Lee la configuración local desde `.env`. | `load_dotenv` en aplicación y administración. |
| Waitress 3.0.2 | Servidor WSGI que recibe HTTP y ejecuta Flask. | Bloque final de `app.py`, función `serve`. |
| Werkzeug | Utilidades de seguridad, entre ellas hash y verificación de contraseñas. Dependencia de Flask. | `generate_password_hash`, `check_password_hash`. |
| cryptography 50.0.2 | Soporte criptográfico para modos de autenticación que puede usar el controlador MySQL. | Dependencia directa en `requirements.txt`. No es la función de hash de usuarios web. |
| pytest | Ejecuta pruebas automatizadas de integración. No se exige al usuario diario. | `tests/test_integration.py`. |
| `venv` y `pip` | Aíslan e instalan bibliotecas Python. | Procedimiento de instalación. |
| PowerShell y archivos CMD | Preparación, comandos y accesos de arranque/parada en Windows. | Scripts e instrucciones. |
| Navegador | Cliente que presenta HTML y envía formularios. También se usó para revisión visual. | Acceso por localhost. |
| Codex | Asistencia para analizar los archivos, escribir/adaptar código, documentación y pruebas. | Proceso de desarrollo; no es un servicio requerido en ejecución. |

Waitress es un servidor WSGI compatible directamente con Windows; Flask recibe de él las solicitudes. [Documentación oficial de Flask sobre Waitress](https://flask.palletsprojects.com/en/stable/deploying/waitress/).

### Herramientas originales frente a herramientas de ejecución

- **PyQt6:** estaba en `nuevainterfaz.py`. Se conserva como antecedente y referencia; no forma parte de la interfaz web actual.
- **MySQL Workbench:** fue indicado como herramienta del proyecto original para administrar la base. Es opcional en la nueva instalación. En esta adaptación se trabajó con MySQL mediante el controlador Python y herramientas de línea de comandos; no debe afirmarse que la página depende de Workbench.
- **Visual Studio Code:** fue el editor indicado en el proyecto original y sirve para estudiar/modificar la entrega. No ejecuta por sí mismo el servidor ni sustituye Python. No es necesario instalarlo para usar la aplicación.
- **No se usaron React, Django, FastAPI, SQLAlchemy, Bootstrap ni una base SQLite** en esta implementación. No los incluyas en una diapositiva como parte del sistema.

## 3. Arquitectura: recorrido de una solicitud

```text
Persona
   ↓ pulsa un enlace o envía un formulario
Navegador: HTML + CSS + JavaScript
   ↓ HTTP a 127.0.0.1:5050
Waitress
   ↓ ejecuta la aplicación WSGI
Flask / app.py: ruta, sesión, permiso y validación
   ↓ consultas sencillas o llamada a una operación de negocio
services.py: recepción, ajuste, producción o venta
   ↓
db.py: conexión y transacción con PyMySQL
   ↓
MySQL: tablas, relaciones y datos persistentes
   ↑ resultados
Jinja genera la página / Flask redirige
   ↑
El navegador muestra la respuesta
```

En una consulta sencilla, `app.py` puede llamar directamente a `rows` o `one`; no todas las consultas pasan por `services.py`. Por eso conviene describirlo como una **separación práctica de responsabilidades**, no como una arquitectura estricta donde cada operación atraviesa todas las capas.

La interfaz se renderiza principalmente en el servidor. No es una SPA ni una API REST completa. Los formularios HTML usan GET para consultar y POST para modificar. `/health` es una respuesta JSON pequeña para comprobar disponibilidad.

El navegador no se conecta directamente a MySQL y no recibe su contraseña. `.env` se lee en el servidor y no se publica como recurso estático.

## 4. Cómo orientarte en el proyecto

| Archivo | Qué estudiar | Pregunta que resuelve |
|---|---|---|
| `app.py` | Rutas, protección, formularios, consultas, respuestas y exportaciones. | ¿Qué pasa cuando se abre una pantalla? |
| `services.py` | `number`, `claim`, `receive`, `adjust`, `produce`, `sell`. | ¿Cómo se modifica el negocio sin inconsistencias? |
| `db.py` | `connect`, `transaction`, `rows`, `one`. | ¿Cómo se conecta, confirma y revierte MySQL? |
| `schema.py` | Extracción del SQL y tablas `kc_*`. | ¿Cómo se instala sin borrar la base original? |
| `manage.py` | `init`, `migrate`, `backup`. | ¿Cómo se administra la instalación? |
| `templates/base.html` | Estructura común, navegación, usuario y mensajes. | ¿Por qué las pantallas comparten diseño? |
| `templates/macros.html` | Campos y estados vacíos reutilizables. | ¿Cómo se evita repetir formularios? |
| `templates/operation.html` | Filas de insumos o productos. | ¿Cómo se presenta una operación con varias líneas? |
| `templates/calendar.html` | Días, actividades y navegación mensual. | ¿Cómo se muestra el cronograma? |
| `static/app.js` | Eventos del navegador. | ¿Qué parte interactiva ocurre sin guardar aún en MySQL? |
| `tests/test_integration.py` | Fixtures y casos reales de prueba. | ¿Qué evidencia respalda que funciona? |

En VS Code puedes usar **Ctrl + Shift + F** para buscar, por ejemplo, `def sell`, `FOR UPDATE`, `def transaction` o `/ventas/nueva`. Es más útil conocer estas funciones que memorizar números de línea, que cambian al editar.

## 5. Modelo de datos y relaciones

### Nueve tablas originales

| Tabla | Significado |
|---|---|
| `categorias` | Agrupa materiales por sector GRANEL o UNIDADES. |
| `items` | Catálogo de materias primas/insumos y su unidad de medida. |
| `lotes_insumo` | Entradas por lote con cantidad, fechas, ubicación y estado. |
| `productos_terminados` | Productos vendibles y volumen por unidad. |
| `ordenes_produccion` | Registro de un lote de producto terminado y sus unidades producidas. |
| `trazabilidad_produccion` | Relaciona una orden con cada lote de insumo consumido y su cantidad. |
| `clientes` | Datos opcionales del comprador. |
| `ventas` | Cabecera: fecha, cliente, total y usuario que registra. |
| `detalle_ventas` | Productos, cantidades, precios y subtotales de una venta. |

### Siete extensiones de la versión web

| Tabla nueva | Por qué hizo falta |
|---|---|
| `kc_users` | El registro/login anterior no guardaba ni validaba usuarios reales. |
| `kc_events` | No existía una tabla para el calendario. |
| `kc_movimientos` | Registrar recepción, ajuste y consumo con motivo, autor y fecha. |
| `kc_stock_terminado` | Guardar el saldo por orden/lote final; el catálogo de productos no era un stock. |
| `kc_asignaciones_venta` | Vincular detalles vendidos con lotes finales y cantidades. |
| `kc_requests` | Rechazar el mismo envío de una operación crítica dos veces. |
| `kc_migrations` | Registrar la versión de las extensiones instaladas. |

Relación principal que debes poder dibujar:

```text
categorias ──< items ──< lotes_insumo
                            │
                            └──< trazabilidad_produccion >── ordenes_produccion
                                                              │          │
                                          productos_terminados┘          └─ kc_stock_terminado
                                                    │
clientes ──< ventas ──< detalle_ventas ──< kc_asignaciones_venta >── ordenes_produccion
```

`──<` significa «uno puede relacionarse con varios». La tabla de trazabilidad permite que una orden use varios lotes y que un lote de insumo participe en varias órdenes. Las asignaciones permiten relacionar una línea de venta con lotes finales; la interfaz actual selecciona un lote por fila de formulario.

Explica también tres restricciones concretas: código de material único; combinación material/número de lote única; lote terminado único. Las claves foráneas evitan referencias a registros inexistentes.

`kc_requests.usuario_id` se guarda como dato, pero **no tiene clave foránea declarada** en la versión actual. No digas que absolutamente todas las columnas con sufijo `_id` tienen una restricción referencial.

## 6. Las tres vistas originales y su uso real

- `v_inventario_peps`: presenta insumos con saldo positivo y estado DISPONIBLE. La usa el resumen del inicio y el reporte; el inicio añade un filtro de fecha para no presentar vencidos como utilizables. El almacén completo consulta tablas porque necesita también agotados y vencidos.
- `v_alertas_vencimiento`: se conserva, pero la pantalla web usa una consulta propia compartida con el tablero. Corrige el caso de lotes ya marcados VENCIDO que la vista original excluye.
- `v_trazabilidad_senasag`: se conserva y se utiliza en la exportación. La pantalla usa joins equivalentes ampliados con IDs, unidades y enlaces a ventas.

No afirmes que todas las pantallas simplemente muestran una vista SQL. Distingue reutilización de vistas de consultas directas necesarias para la navegación y los filtros.

El nombre PEPS no demuestra que el sistema aplique FIFO: esa vista ordena por fecha de vencimiento antes de ingreso. Además, el consumo se selecciona manualmente. El nombre SENASAG tampoco es una certificación.

## 7. Explicación detallada de una venta

Abre `app.py`, busca `new_sale` y después `services.py`, función `sell`.

1. GET `/ventas/nueva` consulta clientes y lotes terminados con saldo para presentar el formulario.
2. El usuario selecciona lote, cantidad y precio. JavaScript puede añadir filas, pero todavía no modifica MySQL.
3. POST recibe listas de lotes, cantidades y precios; comprueba que sus longitudes coincidan y no superen 100 líneas.
4. La protección general verifica sesión y CSRF; el decorador permite VENTAS o ADMIN.
5. `sell` abre `transaction()` y registra el token con `claim`.
6. Inserta la cabecera de venta inicialmente con total cero, dentro de la transacción aún no confirmada.
7. Para cada lote consulta el saldo con `SELECT ... FOR UPDATE` y valida disponibilidad.
8. Calcula subtotal y total con `Decimal`, inserta detalle y asignación, y descuenta el stock terminado.
9. Actualiza el total de la cabecera.
10. Si no hubo errores, `transaction()` hace `commit`; después Flask redirige al detalle. Ante un error hace `rollback` y nada de esa venta queda confirmado.

Ejemplo exclusivamente didáctico: 2 unidades a Bs. 12,50 producen un subtotal de Bs. 25,00. Si el lote tenía 10, queda con 8. El lote de materia prima no cambia al vender: se descontó antes, durante la producción.

### Por qué `Decimal`

Representa cantidades decimales sin los errores binarios típicos de `float`. Se valida la precisión antes de guardar: normalmente dos decimales para cantidades/importes y tres para volumen unitario de productos. MySQL también usa columnas DECIMAL. No se aceptan valores infinitos, NaN, negativos o unidades fraccionarias donde corresponda.

### Qué resuelve el bloqueo

Si dos solicitudes intentan vender el mismo saldo, el bloqueo de la fila hace que la segunda espere a que la primera termine. Luego lee el saldo actualizado y, si no alcanza, falla. La prueba concurrente comprueba ese caso. Esto no significa que todos los problemas posibles de concurrencia estén resueltos ni que exista reintento automático de deadlocks.

### Dos protecciones distintas contra duplicación

Desactivar el botón en JavaScript ayuda al usuario, pero puede eludirse. La clave primaria de `kc_requests.token` impide confirmar de nuevo el mismo token desde el servidor. Si una operación falla, el token se revierte con ella. Esto evita el reenvío del **mismo formulario**; no detecta que dos formularios nuevos con tokens distintos describan por error la misma venta comercial.

## 8. Producción, ajustes y trazabilidad

`produce` registra producto final, número de lote y cantidad entera producida. Los insumos se ingresan explícitamente: no hay recetas ni proporciones químicas inferidas.

Por cada consumo valida el lote, su estado, fecha de vencimiento, unidad y saldo. Descuenta la cantidad y guarda simultáneamente la relación en `trazabilidad_produccion` y el movimiento de inventario. Finalmente crea `kc_stock_terminado`. Todo está dentro de la misma transacción.

Un ajuste no borra el saldo anterior sin evidencia: `adjust` lee el saldo con bloqueo, calcula la diferencia, exige un motivo y añade un movimiento. Las recepciones también generan movimiento inicial.

Desde el detalle de un lote de insumo puedes ver qué órdenes lo usaron. Desde una orden puedes ver qué ventas registradas recibieron su lote. Las ventas históricas sin asignación no tienen ese recorrido: el programa lo indica y no inventa una relación.

## 9. Calendario y alertas

`planner` calcula semanas y días con el módulo estándar `calendar`, consulta actividades cuyo intervalo cruza el mes y las coloca en sus días. `event` valida y guarda inicio, fin, descripción y estado. Una actividad que empieza en diciembre y termina en enero puede verse en ambos meses.

Los datos permanecen porque están en `kc_events`, no solamente en memoria o en almacenamiento del navegador. Autor y ADMIN pueden editar; los demás usuarios consultan. Completar o cancelar conserva el historial.

Las alertas se calculan al consultar la página, usando la misma consulta para listado y contador: hoy o antes es vencido; hasta 7 días es crítico; hasta 30 días es atención. Se consideran lotes con saldo y también los marcados VENCIDO. No hay un proceso que envíe correos o notificaciones en segundo plano.

La hora se fija en UTC−04:00 tanto en Python como en la sesión MySQL. No se implementó un sistema configurable de zonas horarias internacionales.

## 10. Seguridad: explica lo que sí existe y sus límites

| Medida | Implementación | Lo que no debes afirmar |
|---|---|---|
| Contraseñas con hash | Werkzeug genera/verifica el hash. | No se «descifran» contraseñas ni se guardan para leerlas después. |
| Sesión | Cookie firmada por Flask, HttpOnly, SameSite=Lax; sesión permanente de 8 horas. | Firmada no significa cifrada; no guardes secretos en la cookie. |
| CSRF | Token de sesión comparado en POST. | No sustituye los permisos de usuario. |
| Permisos | Decorador y comprobaciones de rol/autor en servidor. | Ocultar un botón no sería suficiente por sí solo. |
| SQL parametrizado | Los valores del usuario se envían como parámetros `%s`. | No toda cadena SQL es estática: nombres de tablas de catálogos/reportes provienen de listas internas permitidas. |
| Validación de servidor | Cantidades, fechas, estados, relaciones y límites. | La validación HTML por sí sola no protege la base. |
| Escape de salida | Plantillas HTML con escape automático de Jinja. | No es una auditoría completa de todo posible contenido malicioso. |
| Cabeceras HTTP | CSP, bloqueo de marcos, protección de tipo de contenido y no caché. | No convierten HTTP local en HTTPS. |
| Cuenta MySQL limitada | Web con SELECT/INSERT/UPDATE/DELETE y SHOW VIEW. | No debe ejecutar a diario como root. |
| Exposición local | Waitress escucha en 127.0.0.1. | No está preparado sin cambios para publicarse en internet. |

No hay autenticación de dos factores, recuperación de contraseñas en pantalla ni limitación específica de intentos de login. El primer administrador puede crearse cuando no existen usuarios, por alguien con acceso al sitio local. Estas son limitaciones relevantes antes de plantear una publicación o un entorno compartido.

## 11. Cómo se conservó el trabajo previo

El Python y el SQL originales se guardan sin modificaciones en `originales`; se compararon sus huellas SHA-256 con las de los adjuntos. Las capturas también se conservaron.

La interfaz anterior ya tenía estructura de navegación, tarjetas, inventario y trazabilidad, pero dependía de `BDconexion.py`, que no fue entregado. Ventas y acceso de usuarios contenían simulaciones. Por eso se construyó una capa de conexión nueva y se sustituyeron esos comportamientos por operaciones reales.

`schema.py` solo extrae declaraciones CREATE TABLE y CREATE OR REPLACE VIEW del archivo recibido para inicializar una base vacía. Omite DROP DATABASE, CREATE DATABASE, USE e INSERT del original. `manage.py` crea de forma controlada la base seleccionada. Las ampliaciones usan prefijo `kc_` para distinguirlas.

Para una base existente, `migrate` realiza primero una copia y añade extensiones sin reemplazar las tablas/vistas originales. Es un mecanismo sencillo de migración de esta versión, **no** Alembic ni un motor completo de evolución de esquemas. El DDL de MySQL puede confirmar cambios implícitamente: no prometas que una inicialización interrumpida se revierte como una venta.

## 12. Pruebas y evidencia

Durante la entrega se aprobaron **18 pruebas de integración contra MySQL real**. Incluyen rutas vacías, ciclo completo por servicios y formularios, reversión de operaciones, concurrencia, tokens, alertas, calendario, permisos, migración y exportación. Se usaron bases independientes, nunca datos comerciales inventados.

En el navegador se revisaron el acceso, el tablero y el calendario, y se guardó una actividad de prueba. Se verificó su persistencia después de recargar y de reiniciar MySQL. La base del negocio quedó vacía para el primer uso.

Si te preguntan «¿está todo probado?», una respuesta precisa es: «Tenemos pruebas de los flujos y errores principales y una revisión visual. No es una prueba de carga ni una auditoría de seguridad; tampoco se validaron todas las versiones de sistema operativo y MySQL». En la otra PC debes repetir los pasos de instalación y registrar su propio resultado.

## 13. Guion de defensa de 8–10 minutos

| Tiempo aproximado | Qué mostrar y explicar |
|---|---|
| 0:00–1:00 | Problema y objetivo: controlar existencias, ventas y origen por lote. |
| 1:00–2:00 | Antecedentes: PyQt6 y SQL recibidos; qué se conservó y qué faltaba. |
| 2:00–3:00 | Arquitectura navegador → Waitress/Flask → servicios/PyMySQL → MySQL. |
| 3:00–4:00 | Modelo de datos: insumos y productos terminados son inventarios diferentes. |
| 4:00–6:00 | Demostración en base de práctica: recepción → producción → venta → trazabilidad. |
| 6:00–7:00 | Mostrar `sell` y `transaction`: bloqueo, Decimal, commit/rollback y token. |
| 7:00–8:00 | Alertas y calendario; recargar para demostrar persistencia. |
| 8:00–9:00 | Resultado de pytest, ejemplo de venta rechazada sin saldo negativo. |
| 9:00–10:00 | Límites y mejoras futuras, sin atribuir funciones inexistentes. |

Antes de la exposición, prepara categorías, materiales, productos y usuarios únicamente en la base de práctica de la primera guía. No uses identidades o datos comerciales reales para una demostración pública. Cierra archivos con credenciales antes de compartir pantalla.

## 14. Preguntas que podrían hacerte

**¿Por qué Python y Flask?** Python ya formaba parte del trabajo previo. Flask permite organizar rutas, plantillas y formularios para una aplicación local de tamaño moderado con una estructura directa. No significa que sea la única alternativa.

**¿Por qué no continuar con PyQt6?** El objetivo cambió a una web local. Se reutilizaron referencias visuales y de datos, pero los widgets de escritorio no son elementos del navegador.

**¿Cuál es la diferencia entre MySQL y Workbench?** MySQL Server almacena y procesa los datos. Workbench es una herramienta cliente para administrarlos. La web utiliza PyMySQL para hablar con el servidor.

**¿Qué hace Waitress que no hace Flask?** Waitress atiende las conexiones HTTP y llama a Flask mediante WSGI. Flask decide qué ruta, validación y respuesta corresponden.

**¿Por qué dos tablas para una venta?** Una cabecera contiene los datos comunes; los detalles permiten varios productos sin repetir fecha, cliente y usuario por cada producto.

**¿Cómo se impide vender más de lo disponible?** Se bloquea la fila de stock, se valida su saldo y se descuenta dentro de la misma transacción. No se confía solo en la cantidad mostrada al abrir el formulario.

**¿Qué pasa si falla la tercera línea de una venta?** La transacción revierte también las dos primeras, la cabecera y sus descuentos, siempre que el fallo ocurra antes de confirmar.

**¿Por qué la venta no descuenta materias primas?** Porque ya se descontaron cuando se fabricó el lote terminado. Descontarlas otra vez duplicaría el consumo.

**¿Dónde están las recetas?** No existen en el material recibido ni se añadieron. Los consumos los registra la persona responsable; el sistema verifica consistencia del inventario, no una formulación química.

**¿PEPS está automatizado?** No. Los lotes se seleccionan manualmente. La vista heredada prioriza vencimiento y no demuestra FIFO estricto.

**¿Cómo sabe el calendario qué mostrar?** Consulta `kc_events` para actividades que se solapan con el mes y genera las celdas con `calendar` de Python.

**¿Las alertas se actualizan aunque no abra la página?** La condición se calcula con la fecha actual al consultar. No hay envío automático de mensajes ni un servicio de notificaciones.

**¿Puedo entrar desde mi teléfono?** La configuración actual solo escucha en la misma PC. Acceso por red requeriría configurar y revisar exposición, autenticación y transporte; no basta con copiar el enlace 127.0.0.1.

**¿Qué parte hiciste con ayuda de IA?** La adaptación y documentación se desarrollaron con asistencia de Codex. Tu defensa debe demostrar que entiendes los archivos, puedes seguir una operación y sabes explicar sus límites; no atribuyas a trabajo manual exclusivo lo que tuvo asistencia.

**¿Cómo demostrarías que no son datos de una maqueta?** Registra una operación en la base de práctica, consulta su fila en MySQL, recarga y reinicia. Los valores deben persistir y coincidir con la interfaz.

**¿Está terminado para cualquier negocio?** No. Resuelve este alcance inicial de operación local. No incluye anulaciones/devoluciones, facturación fiscal, ventas de producto líquido a granel, recetas, metas ni edición completa de catálogos.

## 15. Mejoras futuras que puedes proponer con honestidad

1. Edición de catálogos con reglas y auditoría; desactivación de usuarios y recuperación de acceso.
2. Anulación/devolución mediante movimientos compensatorios, conservando el historial.
3. Stock mínimo y vencimientos de productos terminados, que no están modelados como vencimientos de lote final en esta entrega.
4. Paginación e índices ajustados a consultas frecuentes para volúmenes mayores.
5. Política de consumo acordada con el negocio, antes de automatizar FIFO o FEFO.
6. Migraciones versionadas más completas y pruebas de restauración de respaldos.
7. Pruebas de carga, accesibilidad, seguridad y despliegue antes de habilitar acceso externo.

Aprende primero a explicar el recorrido de una venta, una producción y una actividad. Después estudia el resto de rutas. Esa comprensión es más sólida que memorizar una lista de bibliotecas.
