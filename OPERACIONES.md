# Controles, datos y resultados

| Control | Datos consultados / modificados | Resultado verificable |
|---|---|---|
| Inicio | Ventas, producción, stock terminado, lotes, eventos | Resúmenes del día sin cifras fijas. |
| A granel / Por unidad | Categorías → items → lotes | Tabla filtrada por sector. |
| Buscar / Aplicar / actualizar | Items y lotes | Repite consulta con código, nombre, lote y estado elegidos. |
| Número de lote | Lote, movimientos y consumos | Detalle e historial; enlace a órdenes que lo usaron. |
| Recibir lote | `lotes_insumo`, `kc_movimientos`, `kc_requests` | Lote y movimiento guardados juntos; sin duplicación al reenviar. |
| Ajustar existencia | `lotes_insumo`, `kc_movimientos`, `kc_requests` | Nuevo saldo con motivo, autor y diferencia; rechazo de negativos. |
| Añadir categoría/material/producto/cliente | Tabla de catálogo correspondiente | Registro persistido y listado actualizado; valida relaciones/unidades. |
| Diario / Mensual / Anual | `ventas`, `clientes` | Período seleccionado, suma de cabeceras sin duplicar detalles. |
| Nueva venta / Añadir línea / Quitar línea | Selección de lotes terminados y cliente | Formulario de una o varias líneas con cantidades y precios. |
| Confirmar venta | Ventas, detalles, asignaciones, stock terminado, solicitudes | Todo se confirma o revierte; no hay sobreventa concurrente. |
| Número de venta | Venta, detalles, productos y asignaciones | Importes, producto y lote; historial sin asignación se identifica. |
| Registrar producción / Añadir insumo | Productos y lotes utilizables | Selección manual de consumos, sin recetas deducidas. |
| Confirmar producción | Orden, trazabilidad, lotes, movimientos y stock terminado | Descuento de insumos y creación de saldo terminado atómicos. |
| Buscar trazabilidad / fechas | Órdenes, productos, consumos, items y lotes | Cadena por lote y filtro aplicado. |
| Lote final en trazabilidad | Asignaciones → detalles → ventas → clientes | Ventas efectivamente vinculadas al lote seleccionado. |
| Alertas / Ver todas / alerta individual | Lotes con saldo e items | Misma regla para contador y listado; abre lote afectado. |
| Abrir cronograma | `kc_events` | Calendario mensual de actividades guardadas. |
| Anterior / siguiente / hoy | Fechas del calendario | Navegación temporal sin modificar actividades. |
| Seleccionar día / Nueva actividad | Formulario, luego `kc_events` | Día prellenado; actividad persistente al guardar. |
| Actividad del calendario | `kc_events` | Edición por autor/admin o consulta de solo lectura para otros. |
| Estado completada / cancelada | `kc_events.status` | Conserva historial y cambia representación visual. |
| Descargar CSV | Vista inventario / ventas / vista trazabilidad | Archivo completo en UTF-8; sin aplicar filtros de otras vistas. |
| Crear usuario | `kc_users` | Alta solo por ADMIN con contraseña protegida mediante hash. |
| Crear administrador inicial | `kc_users` | Disponible una sola vez mientras no hay usuarios; bloqueo de concurrencia. |
| Iniciar / cerrar sesión | Usuario / sesión | Verifica contraseña o invalida sesión. |
| Iniciar.cmd / Detener.cmd | Procesos locales | Abre o detiene los servidores conservando MySQL en disco. |

Los formularios de operaciones críticas validan en servidor. Los errores de base no se presentan como resultados vacíos; las acciones prohibidas se rechazan aunque se intente acceder directamente a la ruta.
