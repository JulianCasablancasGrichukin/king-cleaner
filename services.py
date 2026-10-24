from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from db import transaction


def today():
    return datetime.now(timezone(timedelta(hours=-4))).date()


def number(value, whole=False, zero=False, places=2):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError('Introduce una cantidad válida.')
    quantum = Decimal(10) ** -places
    maximum = Decimal(10) ** (10-places) - quantum
    if not result.is_finite() or result < 0 or (not zero and result == 0) or result > maximum:
        raise ValueError('La cantidad está fuera del intervalo permitido.')
    if whole and result != result.to_integral_value():
        raise ValueError('Las unidades deben ser números enteros.')
    if result != result.quantize(quantum):
        raise ValueError(f'Se admiten como máximo {places} decimales.')
    return result


def claim(c, token, user):
    if not token or len(token) != 64:
        raise ValueError('Formulario inválido. Vuelve a abrirlo.')
    c.execute('INSERT INTO kc_requests(token,usuario_id) VALUES(%s,%s)', (token, user))


def receive(item, lot, quantity, entered, expires, tank, user, token):
    entered, expires = date.fromisoformat(entered), date.fromisoformat(expires)
    if entered > today() or expires < entered:
        raise ValueError('Revisa las fechas de ingreso y vencimiento.')
    with transaction() as c:
        claim(c, token, user)
        c.execute('SELECT * FROM items WHERE id=%s', (item,))
        material = c.fetchone()
        if not material:
            raise ValueError('Selecciona un material existente.')
        quantity = number(quantity, whole=material['unidad_medida'] == 'UNIDADES')
        state = 'VENCIDO' if expires <= today() else 'DISPONIBLE'
        c.execute('''INSERT INTO lotes_insumo(item_id,numero_lote,cantidad_inicial,cantidad_actual,
            fecha_ingreso,fecha_vencimiento,tanque_almacenamiento,estado) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',
            (item, lot, quantity, quantity, entered, expires, tank or None, state))
        lot_id = c.lastrowid
        c.execute('INSERT INTO kc_movimientos(lote_id,delta,motivo,usuario_id) VALUES(%s,%s,%s,%s)',
                  (lot_id, quantity, 'Recepción inicial', user))


def adjust(lot_id, balance, reason, user, token):
    if len(reason.strip()) < 5:
        raise ValueError('Explica el motivo del ajuste (mínimo 5 caracteres).')
    with transaction() as c:
        claim(c, token, user)
        c.execute('''SELECT l.*,i.unidad_medida FROM lotes_insumo l JOIN items i ON i.id=l.item_id
                     WHERE l.id=%s FOR UPDATE''', (lot_id,))
        lot = c.fetchone()
        if not lot:
            raise ValueError('El lote no existe.')
        balance = number(balance, whole=lot['unidad_medida'] == 'UNIDADES', zero=True)
        delta = balance - lot['cantidad_actual']
        if not delta:
            raise ValueError('El saldo no ha cambiado.')
        state = 'AGOTADO' if balance == 0 else ('VENCIDO' if lot['fecha_vencimiento'] <= today() else 'DISPONIBLE')
        c.execute('UPDATE lotes_insumo SET cantidad_actual=%s,estado=%s WHERE id=%s', (balance, state, lot_id))
        c.execute('INSERT INTO kc_movimientos(lote_id,delta,motivo,usuario_id) VALUES(%s,%s,%s,%s)',
                  (lot_id, delta, reason, user))


PRODUCTION_MODES = {'FABRICACION':'Fabricación', 'ENVASADO':'Envasado'}


def _production_values(c, product, quantity, consumed, mode, lock=False):
    if mode not in PRODUCTION_MODES:
        raise ValueError('Selecciona fabricación o envasado.')
    quantity = number(quantity, whole=True)
    if not 0 < len(consumed) <= 100:
        raise ValueError('Registra entre 1 y 100 consumos de insumos.')
    try:
        consumed = [(int(source), amount) for source, amount in consumed]
    except (ValueError, TypeError):
        raise ValueError('Selecciona lotes de insumo válidos.')
    if len({source for source, amount in consumed}) != len(consumed):
        raise ValueError('No repitas un lote de insumo; suma su consumo en una fila.')
    c.execute('SELECT * FROM productos_terminados WHERE id=%s', (product,))
    target = c.fetchone()
    if not target:
        raise ValueError('El producto no existe.')
    sources = []
    for lot_id, amount in sorted(consumed):
        c.execute('''SELECT l.*,i.nombre material,i.unidad_medida FROM lotes_insumo l
            JOIN items i ON i.id=l.item_id WHERE l.id=%s''' + (' FOR UPDATE' if lock else ''), (lot_id,))
        source = c.fetchone()
        if not source or source['estado'] != 'DISPONIBLE' or source['fecha_vencimiento'] <= today():
            raise ValueError('Un lote seleccionado no está disponible o ya venció.')
        amount = number(amount, whole=source['unidad_medida'] == 'UNIDADES')
        if amount > source['cantidad_actual']:
            raise ValueError('Stock de insumos insuficiente. No se guardó la producción.')
        sources.append(dict(source, amount=amount, remaining=source['cantidad_actual']-amount))
    return dict(product=target, quantity=quantity, sources=sources, mode=mode,
                mode_label=PRODUCTION_MODES[mode])


def preview_production(product, quantity, consumed, mode):
    with transaction() as c:
        return _production_values(c, product, quantity, consumed, mode)


def produce(product, lot, quantity, consumed, responsible, notes, user, token, mode='FABRICACION'):
    with transaction() as c:
        claim(c, token, user)
        values = _production_values(c, product, quantity, consumed, mode, lock=True)
        c.execute('''INSERT INTO ordenes_produccion(lote_producto_terminado,producto_terminado_id,
            cantidad_producida,responsable,observaciones) VALUES(%s,%s,%s,%s,%s)''',
            (lot, product, values['quantity'], responsible, notes))
        order_id = c.lastrowid
        c.execute('INSERT INTO kc_production_details(orden_id,modalidad) VALUES(%s,%s)', (order_id,mode))
        for source in values['sources']:
            lot_id, amount, remaining = source['id'], source['amount'], source['remaining']
            c.execute('UPDATE lotes_insumo SET cantidad_actual=%s,estado=%s WHERE id=%s',
                      (remaining, 'AGOTADO' if remaining == 0 else 'DISPONIBLE', lot_id))
            c.execute('INSERT INTO trazabilidad_produccion(orden_produccion_id,lote_insumo_id,cantidad_descontada) VALUES(%s,%s,%s)',
                      (order_id, lot_id, amount))
            c.execute('INSERT INTO kc_movimientos(lote_id,delta,motivo,usuario_id) VALUES(%s,%s,%s,%s)',
                      (lot_id, -amount, 'Producción ' + lot, user))
        c.execute('INSERT INTO kc_stock_terminado(orden_id,cantidad_actual) VALUES(%s,%s)', (order_id, values['quantity']))
        return order_id


def sell(client, lines, username, user, token):
    if not lines:
        raise ValueError('Añade al menos una línea de venta.')
    total = Decimal('0')
    with transaction() as c:
        claim(c, token, user)
        c.execute('INSERT INTO ventas(cliente_id,total_venta,usuario_registro) VALUES(%s,0,%s)', (client or None, username))
        sale_id = c.lastrowid
        # Explicit lot selection avoids silently imposing a FIFO/FEFO policy.
        for order_id, qty, price in sorted(lines, key=lambda x: int(x[0])):
            qty, price = number(qty, whole=True), number(price)
            c.execute('''SELECT s.cantidad_actual,op.producto_terminado_id FROM kc_stock_terminado s
                JOIN ordenes_produccion op ON op.id=s.orden_id WHERE s.orden_id=%s FOR UPDATE''', (order_id,))
            stock = c.fetchone()
            if not stock or stock['cantidad_actual'] < qty:
                raise ValueError('Stock terminado insuficiente. La venta no fue guardada.')
            subtotal = qty * price
            total += subtotal
            number(total)
            c.execute('''INSERT INTO detalle_ventas(venta_id,producto_terminado_id,cantidad,precio_unitario,subtotal)
                VALUES(%s,%s,%s,%s,%s)''', (sale_id, stock['producto_terminado_id'], qty, price, subtotal))
            detail = c.lastrowid
            c.execute('INSERT INTO kc_asignaciones_venta(detalle_id,orden_id,cantidad) VALUES(%s,%s,%s)', (detail, order_id, qty))
            c.execute('UPDATE kc_stock_terminado SET cantidad_actual=cantidad_actual-%s WHERE orden_id=%s', (qty, order_id))
        c.execute('UPDATE ventas SET total_venta=%s WHERE id=%s', (total, sale_id))
        return sale_id
