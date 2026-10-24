# Prompt técnico para terminar KING CLEANER como aplicación web local

Preparado a partir de la lectura de `nuevainterfaz.py`, `Base de datos proyecto.sql` y las tres capturas adjuntas a la conversación «Crear prompt web local». La revisión es estática: no se ha ejecutado el programa, conectado a MySQL ni comprobado una base instalada. Este documento prepara una implementación futura; no autoriza a iniciarla hasta que el usuario lo indique.

## 1. Encargo y prioridades

Actúa como desarrollador responsable de adaptar y terminar KING CLEANER, un sistema de control, inventario, ventas y producción. Usa Python y MySQL para entregar una aplicación web local que se abra en el navegador. Conserva el trabajo existente, su modelo de datos, identidad visual y funcionalidades aprovechables. PyQt6 es la interfaz de escritorio de referencia y deberá adaptarse a HTML, CSS y comportamiento web; no es un framework web. MySQL Workbench es la herramienta de administración de la base y Visual Studio Code es el editor del proyecto.

Orden de prioridad confirmado por el usuario y las capturas:

1. Menús Almacén/Inventario, Ventas y Trazabilidad que abran pantallas útiles y consulten las tablas reales.
2. Botones y enlaces operativos, formularios validados y persistencia real.
3. Alertas vinculadas a lotes y vencimientos.
4. Calendario/cronograma de actividades planeadas, accesible desde el recuadro de recordatorios «¡No olvides!» situado a la derecha del inicio.
5. Completar la navegación restante sin pantallas que aparenten funciones inexistentes.
6. Gráficos y estadísticas visuales solamente después de lo anterior. En la captura de mensajes se indica expresamente que son secundarios.

No inventes registros, cifras, clientes, ventas, lotes, contraseñas, fechas, reglas comerciales ni afirmaciones de cumplimiento normativo. Distingue siempre requisito confirmado, hallazgo del archivo y propuesta técnica. Los requisitos de calidad y las extensiones descritas aquí son propuestas para hacer coherente la implementación, no funciones ya verificadas.

## 2. Fuentes y estado real de la aplicación

### Código Python

El archivo importa `DatabaseManager` desde `BDconexion`, pero `BDconexion.py` no está entre los adjuntos. No afirmes que la conexión funciona. Cuando se autorice implementar, busca ese módulo en los archivos entregados; si no está disponible, documenta su ausencia y crea una capa de acceso compatible con el esquema verificado.

Componentes existentes que deben guiar la adaptación:

- `KingCleanerLogoWidget`, `ModernCard` y `StatCard`: logo dibujado, tarjetas y estilo.
- `LoginWindow`, `RegisterWindow` y `AppController`: navegación de acceso y registro. El acceso actual acepta cualquier texto, incluso vacío con el nombre «Administrador»; no valida la contraseña. El registro solamente muestra un mensaje de éxito y vuelve al acceso, sin guardar datos.
- `HomeDashboardView`: estructura del tablero. Consulta inventario mediante `obtener_inventario_resumen("GRANEL")` y, si no obtiene filas, prueba `"UNIDADES"`; muestra hasta cinco registros. El estado «Normal» está fijado en el código.
- `InventoryView`: consulta `obtener_inventario_resumen(self.mode)` para `GRANEL` o `UNIDADES`, presenta lotes y dispone de «Actualizar Tabla».
- `VistaTrazabilidadSENASAG`: consulta `obtener_trazabilidad_senasag()` y presenta siete columnas.
- `SalesView`: filas simuladas, importes cero y fecha fija; no consulta ventas reales.
- `GenericModuleView`: Producción, Alertas, Reportes y Configuración son pantallas genéricas.
- `MainSystemWindow`: barra lateral, submenús, cabecera y navegación por vistas.

Otros pendientes comprobados: fecha y hora fijas en la cabecera; indicadores y barras de ventas fijos; botones Mensual y Anual del gráfico del inicio sin acción conectada; texto de ausencia de alertas sin consulta; producción con valores fijos; ausencia del calendario solicitado. Algunos botones de navegación ya tienen callbacks, pero eso no demuestra que la aplicación pueda ejecutarse sin el módulo de conexión.

### Capturas

La captura de mensajes solicita los menús de almacén, ventas y trazabilidad, las tablas de la base visibles en esos apartados y botones funcionales. La captura anotada pide que el recuadro rosa abra un cronograma tipo calendario de lo que se planea hacer. La imagen grande sirve como referencia visual de inicio, tarjetas, inventario, producción, alertas y trazabilidad.

La imagen contiene cifras, nombres comerciales, lotes, porcentajes y fechas ilustrativos: no los conviertas en registros reales. Usa la marca KING CLEANER según el pedido y el código; no reproduzcas posibles errores tipográficos de la imagen. La frase «Desde la materia prima hasta el cliente» expresa una intención visual, pero el esquema actual no permite reconstruir qué lote terminado recibió cada cliente.

## 3. Esquema SQL verificado

Base declarada: `control_produccion_db`, `utf8mb4`, `utf8mb4_unicode_ci`, tablas InnoDB. Todas las tablas tienen `id INT AUTO_INCREMENT PRIMARY KEY`.

| Tabla | Campos y relaciones relevantes |
|---|---|
| `categorias` | `nombre VARCHAR(50)` único, `sector ENUM('GRANEL','UNIDADES')`, `descripcion TEXT` |
| `items` | `codigo VARCHAR(30)` único, `nombre VARCHAR(100)`, `categoria_id` → categorías, `unidad_medida ENUM('LITROS','UNIDADES')`, `stock_minimo DECIMAL(10,2)` con valor predeterminado 0 |
| `lotes_insumo` | `item_id` → items, `numero_lote VARCHAR(50)`, cantidades inicial y actual `DECIMAL(10,2)`, fechas de ingreso y vencimiento `DATE`, tanque opcional, `estado ENUM('DISPONIBLE','AGOTADO','VENCIDO')`; combinación item/lote única |
| `productos_terminados` | Código único, nombre, `volumen_contenido_litros DECIMAL(10,3)` |
| `ordenes_produccion` | Lote terminado único, producto terminado, `fecha_produccion DATETIME`, `cantidad_producida INT`, responsable y observaciones |
| `trazabilidad_produccion` | Orden de producción, lote de insumo y `cantidad_descontada DECIMAL(10,2)` |
| `clientes` | Nombre obligatorio, NIT/CI, teléfono y dirección opcionales |
| `ventas` | Cliente opcional, `fecha_venta DATETIME`, `total_venta DECIMAL(10,2)`, `usuario_registro VARCHAR(100)` |
| `detalle_ventas` | Venta, producto terminado, cantidad entera, precio unitario y subtotal `DECIMAL(10,2)` |

Conserva las restricciones reales del SQL y no sustituyas nombres de columnas sin migración documentada. Hay borrados en cascada desde órdenes hacia trazabilidad y desde ventas hacia sus detalles; evita que una acción de interfaz elimine accidentalmente el historial. El cliente de una venta puede quedar nulo si se elimina el cliente.

Vistas existentes:

- `v_inventario_peps`: devuelve `item_id`, `codigo`, `material`, `sector`, `lote_id`, `numero_lote`, `cantidad_actual`, `unidad_medida`, `fecha_vencimiento`, `tanque_almacenamiento`. Incluye cantidades positivas y estado `DISPONIBLE`. Ordena por item, vencimiento e ingreso. Aunque se llama PEPS, prioriza vencimiento antes de ingreso; no la describas como FIFO estricto. No excluye por sí sola fechas ya vencidas si el estado sigue siendo disponible.
- `v_alertas_vencimiento`: devuelve lote, código, material, sector, cantidad, unidad, vencimiento, `dias_para_vencer` y `estado_alerta`. Clasifica días ≤ 0 como `CRITICO_VENCIDO`, ≤ 7 como `CRITICO_7_DIAS`, ≤ 30 como `ADVERTENCIA_30_DIAS`, y el resto como `NORMAL`. Solo incluye cantidades positivas con estado `DISPONIBLE`; por ello excluye los lotes marcados explícitamente `VENCIDO` y también devuelve filas normales.
- `v_trazabilidad_senasag`: devuelve `lote_producto_final`, `producto`, `fecha_produccion`, `unidades_envasadas`, `insumo_utilizado`, `tipo_insumo`, `lote_origen_insumo`, `tanque_origen`, `cantidad_descontada`. Une órdenes, productos, consumos, lotes, items y categorías mediante joins internos. Una orden sin consumos no aparecerá en esta vista.

El SQL aporta tres categorías, cuatro items y cinco lotes de insumos como carga inicial. Sus fechas dependen de `CURDATE()` y de intervalos relativos al día de ejecución. No contiene inserciones de productos terminados, órdenes, trazabilidad, clientes ni ventas. No puede asumirse que esos registros iniciales describan existencias comerciales actuales ni que ya estén instalados.

## 4. Conservación y migración

El script empieza con `DROP DATABASE IF EXISTS control_produccion_db`. No lo ejecutes sobre una base existente. Conserva intactos los originales y trabaja en una carpeta de aplicación web separada.

Antes de modificar una base instalada, verifica servidor, nombre de base, tablas, vistas y versión; realiza una copia de seguridad verificable. Compara el esquema instalado con el adjunto, registra diferencias y prepara migraciones incrementales con control de versión. No recrees tablas, no borres registros ni reinsertes automáticamente la carga inicial. Separa instalación vacía, migraciones y datos de prueba. Ensaya migraciones y pruebas sobre una base aislada.

No hace falta cambiar MySQL por otra base. No atribuyas al archivo adjunto información que solo podría conocerse mediante una conexión real.

## 5. Arquitectura propuesta

Como opción sencilla, utiliza Flask, plantillas Jinja, CSS y JavaScript moderado con un controlador MySQL compatible. Esta elección es una propuesta técnica; Python y MySQL sí son requisitos. Si los archivos adicionales revelan una arquitectura web existente, prioriza reutilizarla y explica cualquier cambio.

Separa configuración, acceso a datos, servicios de negocio, rutas, plantillas y recursos estáticos. Evita lógica SQL dentro de las plantillas. Usa consultas parametrizadas, transacciones y tipos decimales para cantidades e importes; no calcules dinero con coma flotante binaria.

Configura conexión y clave de sesión mediante variables de entorno, con archivo de ejemplo sin secretos. Usa una cuenta de base con permisos mínimos adecuados. Arranca en `127.0.0.1`, con puerto documentado y recursos locales para el funcionamiento habitual sin CDN. No despliegues en internet. Incluye instrucciones reproducibles para Windows, entorno virtual, dependencias, configuración MySQL, migraciones, arranque y parada. El modo de depuración debe ser explícito, no obligatorio.

## 6. Navegación e identidad visual

Mantén interfaz en español, barra lateral, cabecera, bienvenida, tarjetas claras y panel derecho. Conserva los colores del código como referencia: fondo `#FCFCF4`, azul principal `#020378`, azul claro `#0284C7`, dorado `#FFBB33`, naranja `#FF6B00`, texto `#0F172A` y tarjetas blancas. Adapta el logo existente a un recurso web sin depender de PyQt6; no des por disponible un logo original de alta resolución.

Menús: Inicio; Ventas → Diario/Mensual/Anual; Almacén/Inventario → Almacén y lotes/A granel/Por unidad; Producción; Trazabilidad; Alertas; Reportes; Configuración; Cerrar sesión. Evita duplicar «Almacén» e «Inventario» como dos sistemas distintos.

Cada enlace debe abrir la vista correspondiente, indicar la sección activa y permitir volver. Los accesos del tablero deben llevar a las mismas vistas y filtros que la barra lateral. Usa fecha y hora actuales con zona configurada; para este proyecto puede proponerse `America/La_Paz`, manteniendo consistencia con MySQL. Presenta moneda en Bs. como en el diseño, sin introducir impuestos o facturación fiscal no solicitados.

Adapta el diseño a pantallas de escritorio de 1280×720 y 1366×768 y a anchos menores sin superponer controles. Incluye etiquetas, foco de teclado, contraste, tablas legibles y desplazamiento cuando sea necesario. Distingue carga, vacío, error y éxito. Un error de conexión nunca debe mostrarse como «Sin registros» o «Todo en orden».

## 7. Almacén e inventario

Relaciona `categorias`, `items` y `lotes_insumo`; reutiliza `v_inventario_peps` para la consulta de disponibles cuando corresponda. Muestra código, material, sector, número de lote, cantidad, unidad, ingreso, vencimiento, estado y ubicación/tanque. Los campos no presentes en la vista se obtendrán mediante una consulta explícita a tablas, no mediante valores inventados.

Ofrece filtros por sector, material/código, lote y estado, búsqueda y actualización. La vista de almacén completa debe permitir consultar agotados y vencidos; no puede depender únicamente de una vista que los excluye. Usa «Sin tanque registrado» o equivalente cuando el campo sea nulo; «Almacén Central» aparece como sustituto en el código, pero no es una ubicación acreditada por el SQL.

Para completar operaciones, propone formularios de alta de categorías/items y recepción de lotes, edición controlada de datos descriptivos y ajustes de existencia con motivo. No permitas cambiar saldos históricos silenciosamente. Si implementas ajustes o movimientos auditables, incorpora una tabla mediante migración y registra autor, fecha, lote, cantidad, motivo y referencia. No afirmes que esa tabla ya existe.

Valida obligatoriedad, códigos únicos, lote único por item, cantidades positivas según operación, fechas coherentes y unidades compatibles con el sector. Para UNIDADES exige cantidades enteras en operaciones nuevas, detectando antes posibles fracciones heredadas sin corregirlas automáticamente. No sumes litros y unidades en un mismo total. Conserva por separado el inventario de insumos y el de productos terminados.

## 8. Ventas

Sustituye por consultas reales las cinco filas simuladas de `SalesView`. Usa `ventas`, `detalle_ventas`, `productos_terminados` y `clientes`.

Diario, Mensual y Anual deben permitir elegir el período y aplicar límites de fecha coherentes. Muestra identificador de venta, fecha/hora, cliente cuando exista, usuario, total y detalle con producto, cantidad, precio unitario y subtotal. Una fila de detalle no cuenta como una venta adicional. El total del período debe sumar cabeceras una sola vez, sin multiplicarlo al unir detalles.

Propón «Nueva venta» con cliente opcional, productos reales, cantidades y precios ingresados explícitamente. No existe lista de precios en el esquema: no inventes precios ni asumas un precio de venta persistido en el catálogo. Calcula subtotales y total en el servidor, valida valores y guarda cabecera/detalles en una sola transacción. Evita duplicar la venta al reenviar el formulario.

El esquema no dispone de stock terminado por lote ni de asignación de lotes a líneas de venta. Antes de implementar descuentos de stock o trazabilidad hasta clientes, define una extensión mínima que relacione existencias terminadas y lotes de producción con los detalles vendidos. Una línea puede requerir varios lotes. Las ventas históricas sin asignación deben conservarse con trazabilidad no disponible; no asignes un lote por deducción.

No descuentes una venta directamente de `lotes_insumo`: esos son insumos, no productos terminados. No inventes existencias iniciales a partir de imágenes o ventas antiguas. Si falta información para stock terminado, deja esa limitación explícita y resuelve la decisión con el usuario antes de afirmar que existe control de disponibilidad. Las anulaciones, devoluciones y ventas a granel no están definidas en el material: no agregues reglas comerciales silenciosas.

## 9. Trazabilidad y producción

La consulta prioritaria debe funcionar con `v_trazabilidad_senasag` y permitir buscar por lote final, producto, fecha y lote de insumo. Muestra las siete columnas del código: lote final, producto, fecha de producción, insumo utilizado, sector, lote origen y cantidad descontada. Añade unidades envasadas, tanque y unidad de medida cuando ayuden a interpretar el registro; esta última requiere consultar `items` mediante las relaciones correspondientes.

Permite abrir un detalle que conecte orden de producción → consumos → lotes de insumos → materiales. Mantén la relación inversa para identificar órdenes afectadas por un lote de insumo. Usa IDs en enlaces y consultas, no solo nombres o números de lote, que pueden repetirse entre items.

No prometas certificación ni cumplimiento SENASAG porque la vista tenga ese nombre. La trazabilidad actual llega a producción; la extensión hasta cliente requiere las relaciones adicionales descritas en Ventas.

Para hacer operativa Producción, propone un formulario de producto, lote final único, cantidad producida entera, responsable, fecha y consumos por lote. No hay fórmulas ni recetas: los consumos se ingresan explícitamente, sin inferir proporciones químicas. Valida disponibilidad, vencimiento y unidades; guarda orden, consumos y descuentos de insumos en una transacción. Usa bloqueo de filas o actualización condicional que impida saldos negativos cuando dos operaciones compiten. Un fallo debe revertir todo.

No conviertas automáticamente el orden por vencimiento de la vista en una política de consumo aprobada. Documenta y confirma si se requiere selección manual, PEPS por ingreso o FEFO por vencimiento. Los estados «Pendiente» y «En proceso» y la meta diaria de la imagen no tienen campos en `ordenes_produccion`; requieren ampliación explícita si se implementan. El volumen producido puede calcularse como cantidad de unidades × volumen unitario, sin confundir unidades con litros.

## 10. Alertas

Conecta tarjeta, contador de menú y pantalla de alertas a la misma consulta o servicio. Muestra lote, material, sector, vencimiento, días restantes, cantidad y gravedad; permite abrir su detalle. «Ver todas» y cada alerta deben funcionar.

Como comportamiento de partida, documenta los umbrales existentes del SQL: hoy o antes, crítico vencido; 1–7 días, crítico; 8–30, advertencia; más de 30, normal. No cuentes `NORMAL` como alerta activa. Explica que la regla actual considera vencido un lote que vence hoy; cualquier cambio de criterio debe ser explícito.

Corrige mediante consulta complementaria o migración el punto ciego de la vista: un lote con saldo y estado `VENCIDO` no debe desaparecer de la atención solo porque fue actualizado su estado. Los agotados sin saldo no generan alerta de existencia vencida. No permitas consumir un lote vencido por tener todavía el estado `DISPONIBLE`.

Si se incluyen alertas de stock bajo, usa `stock_minimo` y define de forma visible el criterio, la agregación por item y si se excluyen lotes no utilizables. Esta ampliación no debe confundirse con una función ya implementada. No uses el «Normal» fijo del tablero original.

## 11. Calendario y cronograma

Añade el recuadro «¡No olvides! / Recordatorios» en la columna derecha, conforme a la zona marcada en rosa. Al pulsarlo, abre un calendario o panel de cronograma de actividades previstas.

Como propuesta funcional mínima: vista mensual, navegación anterior/siguiente/hoy, selección de día y lista de actividades; crear, consultar, editar, completar y cancelar actividades. Campos propuestos: título obligatorio, descripción opcional, inicio, fin o modalidad de día completo, estado, responsable opcional y fechas de creación/actualización. Decide y documenta si cada actividad tiene hora o solo fecha; valida que el fin no preceda al inicio.

No existe tabla de recordatorios en el SQL. Añádela mediante migración y persiste cambios en MySQL, de modo que sobrevivan a recargar o reiniciar. Distingue actividades planificadas de vencimientos automáticos de lotes. Si muestras vencimientos en el calendario, enlázalos al lote real y evita duplicarlos cada vez que se consulta. No inventes una agenda, metas o tareas de ejemplo en la base del usuario. Sin actividades, muestra un estado vacío y la acción de crear.

El alcance confirmado no exige correos, notificaciones externas, integración con Google Calendar ni un servicio de tareas en segundo plano.

## 12. Acceso, módulos restantes y datos honestos

Si se conserva el acceso, reemplaza la simulación por usuarios persistentes, contraseñas con hash seguro, sesiones y cierre efectivo. El esquema no contiene usuarios ni roles; añádelos mediante migración. El registro del escritorio ofrece Operario de Almacén, Administrador de Planta y Encargado de Ventas, pero no define permisos. Propón una matriz de permisos y resuelve su alcance; no atribuyas facultades concretas a esos roles como si estuvieran acordadas. No permitas que un registro abierto se asigne privilegios administrativos. Prepara una forma documentada de crear el administrador inicial sin credenciales predeterminadas públicas.

Protege las operaciones que modifican datos frente a solicitudes no autorizadas y CSRF; valida siempre en servidor y escapa el contenido mostrado. No expongas credenciales, consultas internas o trazas técnicas en mensajes al usuario.

Reportes puede ofrecer listados filtrados/exportables de los módulos ya existentes; Configuración puede mostrar parámetros realmente soportados. Estas son propuestas de alcance mínimo. No completes dichos menús con botones que solo muestren mensajes de éxito sin operación. Si alguna función queda fuera de la entrega, indícalo con precisión y no la declares terminada.

Los indicadores deben proceder de datos reales. Ventas de hoy: suma de ventas del período. Producción de hoy: cálculo por órdenes/producto. Alertas: recuento con regla documentada. «Productos en stock» exige definir si cuenta referencias o unidades; no mezcles insumos y productos. No muestres porcentajes de variación sin ambos períodos ni dividas por cero. Una base vacía puede mostrar cero después de una consulta correcta; una consulta fallida debe mostrar error o dato no disponible.

## 13. Matriz de comprobación y pruebas

Cuando se autorice implementar, crea una matriz de cada control visible con su destino o acción, entrada, tablas afectadas y resultado esperado. Verifica como mínimo:

- Navegación completa, submenús y accesos desde inicio; filtros Diario/Mensual/Anual coherentes entre tabla y resumen.
- Inventario correspondiente al sector seleccionado, actualización después de cambios y consulta de lotes agotados/vencidos.
- Recepción y ajustes válidos persistidos; rechazo de duplicados, cantidades inválidas y datos incompletos sin cambios parciales.
- Ventas con varios detalles, importes decimales correctos y total sin duplicación; comportamiento sin productos o sin ventas; prevención de doble envío.
- Trazabilidad con múltiples insumos por orden y múltiples órdenes por insumo, sin atribuir clientes no relacionados.
- Producción sin stock suficiente o con lote vencido, y reversión completa ante fallo; concurrencia sin saldos negativos.
- Alertas en límites de 0, 7, 8, 30 y 31 días, lotes vencidos con saldo y agotados sin saldo; consistencia de contadores.
- Calendario en cambios de mes/año, guardado, edición y finalización; persistencia tras reiniciar y fechas inválidas rechazadas.
- Autenticación real, rechazo de credenciales inválidas, cierre y restricciones de permisos si se implementan.
- Base vacía, conexión fallida, errores de escritura y reintentos con mensajes útiles y sin falsa confirmación.
- Migraciones sobre una copia con datos existentes: registros y relaciones conservados.

Usa datos sintéticos solo en una base de pruebas separada, identificada como tal; nunca los presentes como datos del negocio. Ejecuta pruebas de integración contra MySQL y una revisión visual/funcional en navegador. No sustituyas la prueba de persistencia por comprobar únicamente que una página carga. Reporta lo ejecutado, lo aprobado, los fallos y las verificaciones impedidas por falta de entorno.

## 14. Entrega y decisiones pendientes

La implementación futura debe entregar código web organizado, originales conservados, dependencias, configuración de ejemplo sin secretos, migraciones, instrucciones locales y resultados de pruebas. Incluye un mapa de reutilización entre clases/vistas del escritorio y páginas/servicios web, y documenta cualquier extensión del esquema.

Antes de cerrar decisiones que afecten datos o reglas de negocio, resuelve:

1. Disponibilidad de `BDconexion.py`, otros módulos y recursos originales; existencia y estado real de MySQL y su base. Solicita configuración local cuando haga falta, sin pedir contraseñas en el chat.
2. Si la carga inicial del SQL es demostrativa o corresponde a inventario real.
3. Alcance operativo de las ventas: productos envasados del esquema actual, stock terminado, asignación por lote y posible venta a granel, que no está modelada como tal.
4. Política de selección de lotes y criterio de vencimiento en la fecha límite.
5. Permisos de roles, política de registro y responsables de actividades.
6. Alcance adicional de estados de producción, reportes, ajustes y anulaciones, sin desplazar las prioridades confirmadas.

No bloquees consultas de inventario, ventas históricas, trazabilidad existente o diseño de navegación por decisiones que solo afecten funciones posteriores. Señala qué decisión condiciona cada operación. No declares terminada una función cuyo flujo principal dependa de simulaciones o de una integración sin probar.

Comienza a implementar y probar únicamente cuando el usuario lo indique. Hasta entonces, el resultado es este prompt técnico y la identificación de requisitos, limitaciones y decisiones pendientes.
