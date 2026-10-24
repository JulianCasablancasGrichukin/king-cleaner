# Historial de cambios aprobados

## 2026-10-24 — Separación de insumos, productos terminados y producción

**Estado:** aprobado por el Product Owner para registrar en Git y publicar en
GitHub. Incluye el recorrido guiado descrito más abajo.

### Organización y operación

- Insumos y materiales reúne catálogo, recepción y existencias por lote. Incluye
  materias primas, líquidos preparados y materiales de empaque.
- Productos terminados tiene acceso propio al catálogo y una nueva pantalla de
  existencias (`/productos/existencias`). Muestra lotes con saldo positivo,
  presentación, modalidad de origen y acceso a trazabilidad; permite buscar por
  producto, código o lote. ADMIN y VENTAS pueden continuar a una venta.
- Producción contiene Registrar fabricación o envasado e Historial de producción.
  El catálogo de productos ya no pertenece a este módulo.
- Fabricación registra materias primas y empaques consumidos para obtener unidades
  terminadas. Envasado registra líquido ya preparado y empaques consumidos para
  obtener esas unidades. Ambas modalidades conservan consumos manuales.

### Registro en tres pasos

1. Qué obtuviste: modalidad, producto terminado, lote, unidades y observaciones.
2. Qué utilizaste: insumos y lotes, saldo disponible y cantidad utilizada con su
   unidad explícita. Las unidades de empaque exigen cantidades enteras; los litros
   admiten dos decimales. Se detectan lotes repetidos.
3. Revisar y confirmar: el servidor valida y muestra las unidades que se añadirán,
   cada descuento y el saldo previsto. Revisar no crea órdenes ni movimientos.
   Corregir datos conserva la información. Confirmar vuelve a validar y bloquea
   los lotes antes de registrar toda la operación en una transacción.

Los errores de validación conservan los datos del formulario. JavaScript ofrece
la navegación entre los dos primeros pasos; sin JavaScript ambos aparecen juntos
y la revisión del servidor sigue disponible. El envío conserva la acción elegida
(revisar, corregir o confirmar) al desactivar los botones contra dobles clics.

### Datos y migración

- Extensión `kc_production_details`: relaciona cada orden nueva con FABRICACION o
  ENVASADO. No se altera la estructura de las tablas originales.
- Migración versión 2 añadida a `schema.py`, tanto para instalaciones nuevas como
  para `python manage.py migrate` en instalaciones existentes.
- Base local respaldada antes de migrar; se compararon las cantidades de registros
  de las tablas existentes antes y después, sin cambios.
- Órdenes antiguas sin modalidad se muestran como «Modalidad no registrada»;
  no se deduce su origen ni se generan existencias históricas.

### Validación y límites

- **30 pruebas de integración aprobadas** en MySQL aislado. Cubren fabricación,
  envasado, revisión sin escrituras, corrección, confirmación, prevención de doble
  envío, validación de unidades/lotes y cambio de saldo entre revisión y guardado.
- La suite conserva las verificaciones de concurrencia, transacciones, permisos,
  ventas y trazabilidad existentes.
- Prueba real del navegador en una base `king_cleaner_test_ui_*`: inicio de sesión,
  elección de envasado, consumo de líquido y empaques, revisión, confirmación y
  comprobación del lote terminado con diez unidades y origen Envasado.
- Servidor local reiniciado después de la migración; `/health` responde OK.

La fabricación registrada termina en unidades envasadas listas para vender.
Elaborar a granel, almacenar ese lote intermedio y envasarlo en otra operación
requeriría un modelo adicional. No se implementan recetas, conversiones automáticas
ni comprobaciones de rendimiento químico. El volumen por unidad describe la
presentación, no determina automáticamente los consumos. La compra para reventa de
productos ya terminados tampoco se añade en este cambio.

## 2026-10-24 — Productos y recorrido guiado hasta la venta

**Estado:** propuesta inicial implementada y ampliada por la separación de módulos
descrita arriba; aprobada como parte del conjunto.

### Problema y resultado

Al intentar vender sin existencias, la aplicación enviaba a Producción con un
mensaje genérico que no explicaba cómo crear un producto ni preparar los insumos.
Ahora distingue la ficha del producto, la producción que genera existencias y la
venta que las descuenta. El siguiente paso depende de los datos actuales.

### Cambios realizados

- Producción incluye los submenús Productos y Registro de producción. El catálogo
  de productos activa Producción en lugar de Almacén.
- Productos tiene presentación propia, botón Nuevo producto, formulario Guardar
  producto y explicación del contenido en litros por unidad. Se separa de las
  pestañas Categorías y Materiales. Conserva la ruta `/catalogos/productos`.
- Crear un producto conserva el alta de su ficha sin generar existencias. Tras
  guardarlo se explica que falta registrar producción y se ofrece continuar.
- Producción muestra una guía visual de tres pasos y detecta si falta crear un
  producto, categoría, material o recibir insumos utilizables. Si los requisitos
  están listos, ofrece Registrar producción.
- Nueva producción muestra la guía en vez de un formulario incompleto cuando no
  hay productos o insumos utilizables.
- Nueva venta sin stock muestra la guía en vez del formulario de venta. Distingue
  ausencia de productos, producción aún no registrada, existencias agotadas y
  producción histórica sin saldo registrado. Conserva el motivo de falta de stock
  aunque también falten insumos para reponerlo.
- Los catálogos de almacén ofrecen acceso a Recibir insumos para continuar la
  preparación. Se mantienen los accesos existentes desde inventario.
- VENTAS consulta productos y producción, pero no ve botones para crear productos,
  recibir insumos o producir. Se le indica solicitar la preparación a Almacén o
  ADMIN. Los permisos se siguen validando también en el servidor.

### Implementación y conservación

`app.py` centraliza la detección del siguiente paso. `products.html` reutiliza el
listado y formulario de `catalog.html`; `workflow_guide.html` se comparte entre
Producción y los estados bloqueados de venta/producción. Se actualizan
`base.html`, `production.html`, `operation.html` y los estilos adaptables.

La disponibilidad de insumos exige saldo positivo, estado DISPONIBLE y fecha de
vencimiento posterior a hoy, igual que el formulario de producción existente.
No se modifican el esquema de base de datos, las transacciones, el consumo manual
de lotes ni la trazabilidad. No se crean datos de ejemplo en la base del negocio.

### Validación

- **25 pruebas de integración aprobadas** en una base MySQL separada: las 18
  existentes y siete casos nuevos, incluyendo variantes por rol.
- Comprobación del alta de producto sin stock, preparación por etapas, rechazo de
  insumos que vencen hoy y desbloqueo del formulario con insumos utilizables.
- Comprobación de existencias agotadas incluso sin insumos restantes y distinción
  de órdenes históricas sin stock registrado.
- Revisión visual de Productos y Producción mediante HTML de vista previa con
  perfil ilustrativo, sin crear usuarios ni operaciones en la base del negocio.

## 2026-10-24 — Navegación por grupos y acceso directo a Clientes

**Estado:** aprobado por el Product Owner y registrado en el primer commit del repositorio.

### Problema y resultado

La gestión de clientes solo se abría desde Ventas. Su pantalla compartía los
enlaces de categorías, materiales y productos, y activaba el submenú de Almacén.
Ahora Clientes tiene acceso directo junto a Ventas y una presentación propia.

### Organización del panel

| Grupo | Opciones |
|---|---|
| General | Inicio |
| Gestión comercial | Ventas, Clientes |
| Operaciones | Almacén e inventario, Producción, Trazabilidad |
| Seguimiento | Alertas, Calendario, Reportes |
| Administración | Configuración |

Los enlaces del módulo activo se resaltan y exponen `aria-current="page"`.
Ventas, Almacén, Producción y Calendario mantienen la selección del módulo al
abrir sus pantallas relacionadas. Clientes no activa el submenú de Almacén.
Los separadores se ocultan en pantallas pequeñas para conservar la navegación
horizontal existente.

### Pantalla de Clientes

- Listado con nombre, NIT/CI, teléfono y dirección, sin pestañas de almacén.
- Acceso «Nuevo cliente» que lleva al formulario de la misma página.
- Formulario y botón identificados como «Nuevo cliente» y «Guardar cliente».
- Mensajes específicos: «Todavía no hay clientes» y «Cliente guardado».
- ADMIN y VENTAS pueden registrar clientes; ALMACEN puede consultar.
- Se conserva la dirección `/catalogos/clientes` y el enlace desde Ventas.

No se modificó el esquema de base de datos. Búsqueda, edición e historial de
compras quedan para cambios posteriores.

### Archivos modificados

| Archivo | Responsabilidad |
|---|---|
| `templates/base.html` | Grupos, acceso a Clientes y selección del módulo activo. |
| `templates/catalog.html` | Catálogos de almacén y bloques compartidos de listado/formulario. |
| `templates/clients.html` | Presentación y textos propios de Clientes, reutilizando el catálogo base. |
| `app.py` | Selección de plantilla y confirmación específica al guardar clientes. |
| `static/style.css` | Espaciado de grupos y conservación del menú horizontal en móvil. |

### Validación

- Suite de integración existente: **18 pruebas aprobadas**, contra una base
  MySQL de pruebas separada.
- Comprobación de HTML para ADMIN, VENTAS y ALMACEN: selección de Clientes,
  ausencia de pestañas/submenú de almacén y formulario visible según el rol.
- Comprobación de categorías: selección de Almacén y formulario existente
  conservados.
- Servidor web reiniciado y `GET /health` con respuesta `{"status":"ok"}`.
- Revisión del cambio y aprobación explícita del Product Owner en el chat.

### Registro inicial del repositorio

Este primer commit incluye el código base recibido y la modificación
aprobada. No existe un commit anterior con el que comparar el cambio.
`.gitignore` excluye credenciales, datos MySQL, entorno virtual, cachés y logs;
`.env.example` se conserva como plantilla. No se ha conectado ni publicado el
repositorio en GitHub.
