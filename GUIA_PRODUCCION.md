# Insumos, productos y producción

## Qué se registra en cada apartado

| Apartado | Contenido | Cómo obtiene existencias |
|---|---|---|
| Insumos y materiales | Materias primas, líquidos preparados, envases, tapas y etiquetas. | Mediante Recibir insumos. |
| Productos terminados | Presentaciones listas para vender, por ejemplo Limpiador de 500 ml. | Mediante Registrar fabricación o envasado. |
| Producción | Operaciones realizadas y sus consumos reales. | Descuenta insumos y añade unidades terminadas al confirmar. |
| Ventas | Salidas de productos terminados por cliente y lote. | Descuenta las unidades vendidas. |

Crear una ficha de insumo o producto no crea existencias. Cada presentación tiene
su ficha: 500 ml se registra con 0,500 litros por unidad; 1 litro, con 1,000.

## Preparación inicial

1. En Insumos y materiales, crea las categorías y las fichas de los materiales.
   El sector A granel usa litros; Por unidad usa cantidades enteras.
2. Recibe los lotes con cantidades, fechas y ubicación reales.
3. En Productos terminados → Catálogo de productos, crea las presentaciones que
   vendes con código, nombre y litros por unidad.
4. Abre Producción → Registrar fabricación o envasado.

## Los tres pasos de producción

**Qué obtuviste.** Selecciona Fabricación cuando elaboraste el líquido a partir de
materias primas y obtuviste unidades terminadas. Selecciona Envasado cuando
utilizaste líquido ya preparado. Elige el producto, un lote terminado único y las
unidades obtenidas. Ambas opciones registran operaciones ya realizadas.

**Qué utilizaste.** Selecciona los lotes y cantidades reales. Incluye los empaques
consumidos, si corresponden a la operación. Los saldos y unidades aparecen junto a
cada lote. No sumes litros y unidades en una sola cantidad; son consumos separados.

**Revisar y confirmar.** Comprueba el producto, lote, modalidad, unidades a añadir,
insumos a descontar y saldos previstos. Revisar no guarda movimientos. Usa Corregir
datos para volver o Confirmar producción para guardar. Si otro usuario consumió
los insumos mientras revisabas, el sistema vuelve a comprobarlos y rechaza la
operación cuando el saldo es insuficiente.

## Ejemplo de envasado

Ejemplo ilustrativo; no es una receta ni se carga como dato del negocio:

- Resultado: 10 unidades de Limpiador de 500 ml, lote terminado ENV-001.
- Consumos reales declarados: 5 litros de líquido preparado, 10 envases y 10 tapas.
- Al confirmar: disminuyen los tres lotes de insumos y aparecen 10 unidades en
  Productos terminados → Existencias disponibles.
- Vender 3 unidades deja 7 unidades disponibles de ese lote terminado.

Para fabricación, el resultado también es una presentación terminada, pero los
consumos corresponden a las materias primas y empaques realmente utilizados.

## Consulta, permisos y alcance

Productos terminados muestra existencias positivas y enlaza la trazabilidad del
lote. Producción conserva el historial, incluidas las operaciones agotadas o
antiguas sin saldo registrado. Una operación antigua sin modalidad no se presenta
como fabricación o envasado por deducción.

ADMIN tiene acceso completo. ALMACEN registra insumos, productos y producción;
VENTAS consulta esos apartados y registra ventas. No es necesario conceder permisos
de producción a VENTAS para que pueda consultar existencias.

El sistema no calcula recetas, conversiones ni rendimiento. El contenido por
unidad describe la presentación. Elaborar líquido a granel para almacenarlo y
envasarlo otro día requiere un registro de producto intermedio adicional, que
todavía no forma parte del modelo. No registres ese líquido como unidades listas
para vender ni inventes una recepción para simular su fabricación.

## Actualización de otra instalación

Con la aplicación detenida y una conexión administrativa configurada de forma
privada, ejecuta con el entorno virtual:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

El comando crea una copia lógica antes de añadir las extensiones. La versión 2
añade `kc_production_details` para guardar la modalidad. Las órdenes existentes
se conservan sin rellenar modalidades ni saldos por deducción. Después vuelve a
usar la cuenta de aplicación y reinicia el servidor.
