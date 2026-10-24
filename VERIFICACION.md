# Verificación de la entrega

Fecha: 23/10/2026, hora de Bolivia.

## Resultado

**18 pruebas automatizadas aprobadas contra MySQL real (26,02 segundos en la última ejecución).** No se sustituyó la base por SQLite ni por respuestas simuladas. Las pruebas crean bases independientes cuyo nombre empieza por `king_cleaner_test_`.

Casos verificados:

1. Respuesta correcta de 21 rutas y estados vacíos, incluidos los tres períodos de ventas, formularios, catálogos, calendario, configuración y exportación.
2. Ciclo producción → venta de varias líneas → trazabilidad, con stock e importes decimales correctos.
3. Reversión completa de producción sin stock suficiente.
4. Reversión de ventas parcialmente inválidas y rechazo de reenvío con el mismo token.
5. Dos ventas concurrentes sobre el mismo stock: solo una se confirma si el saldo no alcanza para ambas.
6. Alertas en los límites de 0, 7, 8, 30 y 31 días, incluyendo estado VENCIDO.
7. Rechazo de consumo de lote que vence hoy.
8. Ajuste con diferencia y motivo auditados; rechazo de saldo negativo.
9. Actividad de calendario entre diciembre y enero, edición de estado y rechazo de fechas invertidas.
10. CSRF, cierre de sesión, credenciales incorrectas/correctas y permisos por rol.
11. Creación del primer administrador y cierre de ese flujo cuando ya existe un usuario.
12. Migración repetida que conserva registros existentes; rechazo de inicialización sobre una base no vacía.
13. Rechazo de NaN, infinito, negativos, cero no permitido, exceso de decimales y unidades fraccionarias.
14. Error de conexión mostrado como error 503, sin fingir una lista vacía.
15. Neutralización de fórmulas en cadenas de la exportación CSV.
16. Ciclo completo por formularios HTTP: categoría, material, producto con volumen de tres decimales, recepción, producción y venta; rechazo de línea incompleta.
17. Consulta de una actividad ajena y bloqueo de su edición para un usuario no administrador.
18. Día seleccionado en calendario prellenado a las 09:00–10:00 en la actividad nueva.

## Comprobación en navegador

En una instancia de QA separada se comprobó el acceso real, el tablero sin datos, el acceso desde «Abrir cronograma», la creación de una actividad y su presencia después de recargar. Se inspeccionaron capturas de la pantalla inicial y del tablero. `Vista_previa.png` y `Calendario_prueba.png` pertenecen a esa instancia aislada; su usuario y actividad son de prueba, no del negocio.

La instancia de QA se cerró. La instancia principal quedó abierta en `http://127.0.0.1:5050/primer-acceso`, sin usuario creado, para que el propietario elija sus propias credenciales.

## Reinicio y conservación

- `Detener.ps1` cerró la aplicación y MySQL; `Iniciar.ps1 -NoBrowser` volvió a iniciarlos correctamente.
- `/health` devolvió `status: ok` después del reinicio.
- La actividad de QA siguió existiendo tras reiniciar MySQL, comprobada mediante consulta.
- Las nueve tablas de negocio, usuarios y actividades de la base principal se comprobaron vacías. No se cargaron los INSERT del archivo original ni datos sintéticos en ella.
- La copia lógica generada con `manage.py backup` incluyó declaraciones de tablas y vistas. No se ha ensayado la restauración de una base comercial con datos reales.
- SHA-256 de ambas copias originales, Python y SQL, coincide con los adjuntos recibidos.
- El MD5 del ZIP de MySQL descargado coincide con el publicado para la distribución oficial 8.4.13. No equivale a una verificación de firma digital.

## Alcance de la verificación

No es una auditoría de seguridad, certificación normativa ni prueba de carga. No se probaron dispositivos móviles físicos, recuperación ante un apagado abrupto, grandes volúmenes de registros, MySQL de versiones distintas ni una base antigua del usuario (el usuario confirmó que solo tenía el SQL). Las extensiones que no forman parte de esta versión están enumeradas en `LEEME.md`.
