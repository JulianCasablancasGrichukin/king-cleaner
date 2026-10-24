# Historial de cambios aprobados

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
