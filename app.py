import calendar
import csv
import io
import os
import secrets
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from functools import wraps

import pymysql
from dotenv import load_dotenv
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for, Response
from werkzeug.security import check_password_hash, generate_password_hash

from db import rows, one, transaction
import services

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
local = ROOT / '.local'
local.mkdir(exist_ok=True)
key_file = local / 'session.key'
if not key_file.exists():
    key_file.write_text(secrets.token_hex(32), encoding='utf-8')
app = Flask(__name__)
app.config.update(SECRET_KEY=os.getenv('SECRET_KEY') or key_file.read_text(),
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                  PERMANENT_SESSION_LIFETIME=timedelta(hours=8), MAX_CONTENT_LENGTH=1024*1024)


def now():
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


def field(name, label, kind='text', options=None, value='', required=True, step=None):
    return dict(name=name, label=label, kind=kind, options=options, value=value, required=required, step=step)


def choices(query):
    return [(str(r['id']), r['label']) for r in rows(query)]


def text(name, limit=150):
    result = request.form.get(name, '').strip()
    if not result or len(result) > limit:
        raise ValueError('Completa los campos obligatorios y respeta su longitud máxima.')
    return result


def permission(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if g.user['role'] not in ('ADMIN', *roles):
                abort(403)
            return fn(*args, **kwargs)
        return wrapped
    return decorator


@app.before_request
def protect():
    session.setdefault('csrf', secrets.token_hex(32))
    if request.method == 'POST':
        if not secrets.compare_digest(request.form.get('csrf', ''), session['csrf']):
            abort(400, 'El formulario caducó. Recarga la página.')
    g.user = None
    if request.endpoint == 'static':
        return
    if session.get('user_id'):
        g.user = one('SELECT id,username,fullname,role FROM kc_users WHERE id=%s', (session['user_id'],))
    if not g.user and request.endpoint not in ('login', 'setup', 'health'):
        return redirect(url_for('login'))


@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'; form-action 'self'"
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.context_processor
def common():
    return dict(clock=now(), csrf=session.get('csrf'), user=g.get('user'), token=secrets.token_hex(32))


@app.template_filter('money')
def money(value):
    return f'{value or 0:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')


@app.errorhandler(ValueError)
def validation(error):
    return render_template('error.html', title='Revisa los datos', message=str(error)), 400


@app.errorhandler(pymysql.MySQLError)
def db_error(error):
    app.logger.exception('Database operation failed')
    conflict = isinstance(error, pymysql.IntegrityError)
    return render_template('error.html', title='No se guardaron los cambios' if conflict else 'Base de datos no disponible',
        message='El registro ya existe, el formulario ya fue enviado o hay una relación inválida. Revisa los datos antes de repetir.' if conflict else
        'No fue posible consultar MySQL. Comprueba que el servidor esté iniciado y la configuración local sea correcta. No se mostrarán cifras simuladas.'), 409 if conflict else 503


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(400)
def http_error(error):
    return render_template('error.html', title='Acción no disponible', message={403:'Tu rol no tiene permiso para esta acción.',404:'No encontramos ese registro.',400:'Formulario inválido o caducado. Recarga la página.'}.get(error.code)), error.code


@app.get('/health')
def health():
    one('SELECT version FROM kc_migrations WHERE version=1')
    return {'status':'ok'}


@app.route('/acceso', methods=['GET','POST'])
def login():
    if not one('SELECT id FROM kc_users LIMIT 1'):
        return redirect(url_for('setup'))
    if request.method == 'POST':
        u = one('SELECT * FROM kc_users WHERE username=%s', (request.form.get('username',''),))
        if not u or not check_password_hash(u['password_hash'], request.form.get('password','')):
            flash('Usuario o contraseña incorrectos.', 'error')
        else:
            session.clear()
            session.update(user_id=u['id'], csrf=secrets.token_hex(32))
            session.permanent = True
            return redirect(url_for('home'))
    return render_template('login.html', title='Bienvenido de nuevo', setup=False)


@app.route('/primer-acceso', methods=['GET','POST'])
def setup():
    if one('SELECT id FROM kc_users LIMIT 1'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = text('password', 200)
        if len(password) < 12 or password != request.form.get('confirm'):
            raise ValueError('Usa al menos 12 caracteres y confirma la misma contraseña.')
        # Named lock serializes initial administrator creation.
        with transaction() as c:
            c.execute("SELECT GET_LOCK(CONCAT(DATABASE(),':setup'),5) AS locked")
            if c.fetchone()['locked'] != 1:
                raise ValueError('El alta inicial está en curso. Vuelve a intentarlo.')
            try:
                c.execute('SELECT id FROM kc_users LIMIT 1')
                if c.fetchone():
                    raise ValueError('Ya existe un administrador.')
                c.execute('INSERT INTO kc_users(username,fullname,password_hash,role) VALUES(%s,%s,%s,\'ADMIN\')',
                          (text('username',80), text('fullname'), generate_password_hash(password)))
                c.connection.commit()
            finally:
                c.execute("SELECT RELEASE_LOCK(CONCAT(DATABASE(),':setup'))")
        flash('Administrador creado. Inicia sesión con tus datos.', 'success')
        return redirect(url_for('login'))
    return render_template('login.html', title='Tu espacio de trabajo comienza aquí', setup=True)


@app.post('/salir')
def logout():
    session.clear()
    return redirect(url_for('login'))


ALERTS = '''SELECT l.id,i.nombre material,l.numero_lote,l.cantidad_actual,i.unidad_medida,
    l.fecha_vencimiento,DATEDIFF(l.fecha_vencimiento,CURDATE()) dias,
    CASE WHEN l.fecha_vencimiento<=CURDATE() OR l.estado='VENCIDO' THEN 'Vencido'
    WHEN DATEDIFF(l.fecha_vencimiento,CURDATE())<=7 THEN 'Crítico' ELSE 'Atención' END gravedad
    FROM lotes_insumo l JOIN items i ON i.id=l.item_id
    WHERE l.cantidad_actual>0 AND (l.fecha_vencimiento<=DATE_ADD(CURDATE(),INTERVAL 30 DAY) OR l.estado='VENCIDO')
    ORDER BY l.fecha_vencimiento,l.id'''


@app.get('/')
def home():
    stats = dict(sales=one('SELECT COALESCE(SUM(total_venta),0) n FROM ventas WHERE DATE(fecha_venta)=CURDATE()')['n'],
                 stock=one('SELECT COUNT(*) n FROM kc_stock_terminado WHERE cantidad_actual>0')['n'],
                 production=one('''SELECT COALESCE(SUM(op.cantidad_producida*p.volumen_contenido_litros),0) n
                     FROM ordenes_produccion op JOIN productos_terminados p ON p.id=op.producto_terminado_id
                     WHERE DATE(op.fecha_produccion)=CURDATE()''')['n'])
    alerts = rows(ALERTS)
    inventory = rows('SELECT * FROM v_inventario_peps WHERE fecha_vencimiento>CURDATE() ORDER BY fecha_vencimiento,lote_id LIMIT 5')
    events = rows("SELECT * FROM kc_events WHERE status='PENDIENTE' AND ends_at>=NOW() ORDER BY starts_at LIMIT 3")
    recent = rows('SELECT id,fecha_venta,total_venta FROM ventas ORDER BY fecha_venta DESC,id DESC LIMIT 5')
    return render_template('home.html', title='Inicio', stats=stats, alerts=alerts, inventory=inventory, events=events, recent=recent)


@app.get('/inventario')
def inventory():
    sector, q, state = request.args.get('sector',''), request.args.get('q','').strip(), request.args.get('estado','')
    sql = '''SELECT l.id,i.codigo,i.nombre material,c.sector,l.numero_lote,l.cantidad_actual,i.unidad_medida,
             l.fecha_ingreso,l.fecha_vencimiento,l.estado,l.tanque_almacenamiento
             FROM lotes_insumo l JOIN items i ON i.id=l.item_id JOIN categorias c ON c.id=i.categoria_id WHERE 1=1'''
    params = []
    if sector in ('GRANEL','UNIDADES'):
        sql += ' AND c.sector=%s'; params.append(sector)
    if state in ('DISPONIBLE','AGOTADO','VENCIDO'):
        if state == 'VENCIDO':
            sql += " AND (l.estado='VENCIDO' OR (l.cantidad_actual>0 AND l.fecha_vencimiento<=CURDATE()))"
        elif state == 'DISPONIBLE':
            sql += " AND l.estado='DISPONIBLE' AND l.cantidad_actual>0 AND l.fecha_vencimiento>CURDATE()"
        else:
            sql += " AND l.cantidad_actual=0"
    if q:
        sql += ' AND (i.codigo LIKE %s OR i.nombre LIKE %s OR l.numero_lote LIKE %s)'; params += ['%'+q+'%']*3
    data = rows(sql+' ORDER BY l.fecha_vencimiento,l.id', params)
    return render_template('inventory.html', title='Insumos y materiales', data=data, sector=sector, q=q, state=state)


@app.get('/lotes/<int:lot_id>')
def lot_detail(lot_id):
    lot = one('''SELECT l.*,i.nombre,i.codigo,i.unidad_medida FROM lotes_insumo l
                 JOIN items i ON i.id=l.item_id WHERE l.id=%s''',(lot_id,))
    if not lot: abort(404)
    movements = rows('''SELECT m.fecha,m.delta,m.motivo,u.fullname FROM kc_movimientos m
        JOIN kc_users u ON u.id=m.usuario_id WHERE m.lote_id=%s ORDER BY m.id DESC''',(lot_id,))
    orders = rows('''SELECT op.id,op.lote_producto_terminado,tp.cantidad_descontada FROM trazabilidad_produccion tp
        JOIN ordenes_produccion op ON op.id=tp.orden_produccion_id WHERE tp.lote_insumo_id=%s''',(lot_id,))
    return render_template('lot.html', title=lot['numero_lote'], lot=lot, movements=movements, orders=orders)


@app.route('/recepcion',methods=['GET','POST'])
@permission('ALMACEN')
def receive():
    if request.method=='POST':
        services.receive(text('item'),text('lot',50),text('quantity'),text('entered'),text('expires'),request.form.get('tank','')[:50],g.user['id'],text('token'))
        flash('Lote recibido y movimiento registrado.', 'success'); return redirect(url_for('inventory'))
    return render_template('form.html', title='Recibir insumos', subtitle='Añade materias primas, líquidos preparados o materiales de empaque al almacén de insumos.', fields=[
        field('item','Material','select',choices('SELECT id,CONCAT(codigo,\' · \',nombre,\' / \',unidad_medida) label FROM items ORDER BY nombre')),
        field('lot','Número de lote'),field('quantity','Cantidad recibida','number',step='0.01'),
        field('entered','Fecha de ingreso','date',value=now().date()),field('expires','Fecha de vencimiento','date'),field('tank','Tanque / ubicación',required=False)])


@app.route('/lotes/<int:lot_id>/ajuste',methods=['GET','POST'])
@permission('ALMACEN')
def adjustment(lot_id):
    lot=one('SELECT * FROM lotes_insumo WHERE id=%s',(lot_id,))
    if not lot: abort(404)
    if request.method=='POST':
        services.adjust(lot_id,text('balance'),text('reason',250),g.user['id'],text('token'))
        flash('Ajuste registrado con su motivo.', 'success'); return redirect(url_for('lot_detail',lot_id=lot_id))
    return render_template('form.html',title='Ajustar '+lot['numero_lote'], subtitle='El historial conservará el saldo anterior y la diferencia.', fields=[
        field('balance','Nuevo saldo contado','number',value=lot['cantidad_actual'],step='0.01'),field('reason','Motivo del ajuste')])


CATALOGS = {
 'categorias':('Categorías','categorias',[('nombre','Nombre'),('sector','Sector'),('descripcion','Descripción')]),
 'materiales':('Catálogo de insumos','items',[('codigo','Código'),('nombre','Nombre'),('categoria_id','Categoría'),('unidad_medida','Unidad'),('stock_minimo','Stock mínimo')]),
 'productos':('Catálogo de productos terminados','productos_terminados',[('codigo','Código'),('nombre','Nombre'),('volumen_contenido_litros','Litros por unidad')]),
 'clientes':('Clientes','clientes',[('nombre','Nombre'),('nit_ci','NIT / CI'),('telefono','Teléfono'),('direccion','Dirección')])}


@app.route('/catalogos/<kind>',methods=['GET','POST'])
def catalog(kind):
    if kind not in CATALOGS: abort(404)
    title, table, columns = CATALOGS[kind]
    allowed = g.user['role']=='ADMIN' or (g.user['role']=='ALMACEN' and kind!='clientes') or (g.user['role']=='VENTAS' and kind=='clientes')
    if request.method=='POST':
        if not allowed: abort(403)
        values = []
        for name,label in columns:
            values.append(request.form.get(name,'').strip() if name in ('descripcion','nit_ci','telefono','direccion') else text(name,100 if name=='nombre' else 50))
        if kind=='materiales':
            cat=one('SELECT sector FROM categorias WHERE id=%s',(values[2],))
            if not cat or values[3] != ('LITROS' if cat['sector']=='GRANEL' else 'UNIDADES'):
                raise ValueError('La unidad debe corresponder al sector de la categoría.')
            values[4]=services.number(values[4], whole=values[3]=='UNIDADES',zero=True)
        if kind=='productos': values[2]=services.number(values[2], places=3)
        if kind=='categorias' and values[1] not in ('GRANEL','UNIDADES'): raise ValueError('Sector inválido.')
        with transaction() as c:
            c.execute(f"INSERT INTO {table} ({','.join(x[0] for x in columns)}) VALUES ({','.join(['%s']*len(values))})",values)
        message = {'clientes':'Cliente guardado.', 'productos':'Producto creado. Registra una producción para disponer de unidades para vender.'}
        flash(message.get(kind,'Registro guardado.'), 'success'); return redirect(url_for('catalog',kind=kind))
    fields=[]
    for name,label in columns:
        f=field(name,label,required=name not in ('descripcion','nit_ci','telefono','direccion'))
        if name=='sector': f.update(kind='select',options=[('GRANEL','A granel'),('UNIDADES','Por unidad')])
        if name=='unidad_medida': f.update(kind='select',options=[('LITROS','Litros'),('UNIDADES','Unidades')])
        if name=='categoria_id': f.update(kind='select',options=choices('SELECT id,CONCAT(nombre,\' · \',sector) label FROM categorias'))
        if name in ('stock_minimo','volumen_contenido_litros'): f.update(kind='number',step='0.01' if name=='stock_minimo' else '0.001',value='0' if name=='stock_minimo' else '')
        fields.append(f)
    template = {'clientes':'clients.html','productos':'products.html'}.get(kind,'catalog.html')
    return render_template(template,title=title,columns=columns,data=rows(f'SELECT * FROM {table} ORDER BY id DESC'),fields=fields,allowed=allowed)


def production_guide():
    """Find the first missing prerequisite using production's usable-lot rule."""
    state = one('''SELECT
        EXISTS(SELECT 1 FROM productos_terminados) products,
        EXISTS(SELECT 1 FROM categorias) categories,
        EXISTS(SELECT 1 FROM items) materials,
        EXISTS(SELECT 1 FROM lotes_insumo WHERE cantidad_actual>0
               AND estado='DISPONIBLE' AND fecha_vencimiento>CURDATE()) supplies''')
    if not state['products']:
        return dict(stage='product', title='Primero registra tu producto',
                    body='Crea su ficha con código, nombre y contenido por unidad. Después registra una producción para obtener unidades que puedas vender.',
                    action='Crear producto', url=url_for('catalog',kind='productos')+'#nuevo-registro')
    if not state['supplies']:
        if not state['categories']:
            return dict(stage='supplies', title='Organiza tus insumos',
                        body='Crea una categoría para registrar los materiales que utilizarás en producción.',
                        action='Crear categoría', url=url_for('catalog',kind='categorias'))
        if not state['materials']:
            return dict(stage='supplies', title='Registra los materiales de producción',
                        body='Añade los materiales a su categoría. Luego podrás recibir sus lotes y registrar las cantidades disponibles.',
                        action='Crear material', url=url_for('catalog',kind='materiales'))
        return dict(stage='supplies', title='Necesitas insumos disponibles',
                    body='No hay lotes de insumos disponibles, con saldo y sin vencer. Revisa el almacén o recibe los lotes necesarios para producir.',
                    action='Recibir insumos', url=url_for('receive'))
    return dict(stage='production', title='Ya puedes registrar una producción',
                body='Selecciona el producto, indica las unidades fabricadas y los lotes de insumos realmente utilizados. Al confirmar se crearán las existencias para vender.',
                action='Registrar producción', url=url_for('production_new'))


def sale_guide():
    guide = production_guide()
    if guide['stage']!='product':
        state = one('''SELECT EXISTS(SELECT 1 FROM ordenes_produccion) produced,
            EXISTS(SELECT 1 FROM kc_stock_terminado) tracked''')
        preparation = ' '+guide['body'] if guide['stage']=='supplies' else ''
        if not state['produced']:
            guide.update(title='Todavía no hay producción registrada',
                         body='La ficha del producto ya existe. Registra las unidades fabricadas y sus consumos para disponer de existencias para vender.'+preparation)
        elif state['tracked']:
            guide.update(title='No quedan unidades disponibles para vender',
                         body='Las existencias registradas están agotadas. Registra una nueva producción para reponerlas.'+preparation)
        else:
            guide.update(title='La producción histórica no tiene saldo registrado',
                         body='Hay órdenes antiguas sin existencias terminadas registradas. Registra una nueva producción real; las cantidades históricas no se convierten automáticamente en stock.'+preparation)
    return guide


def period():
    mode=request.args.get('modo','diario')
    selected=date.fromisoformat(request.args.get('fecha') or now().date().isoformat())
    if mode=='mensual':
        start=selected.replace(day=1); end=(start+timedelta(days=32)).replace(day=1)
    elif mode=='anual': start=date(selected.year,1,1); end=date(selected.year+1,1,1)
    else: mode='diario'; start=selected; end=start+timedelta(days=1)
    return mode,selected,start,end


@app.get('/ventas')
def sales():
    mode,selected,start,end=period()
    data=rows('''SELECT v.*,c.nombre cliente FROM ventas v LEFT JOIN clientes c ON c.id=v.cliente_id
        WHERE fecha_venta>=%s AND fecha_venta<%s ORDER BY fecha_venta DESC,v.id DESC''',(start,end))
    return render_template('sales.html',title='Ventas',mode=mode,selected=selected,data=data,total=sum(x['total_venta'] for x in data))


@app.route('/ventas/nueva',methods=['GET','POST'])
@permission('VENTAS')
def new_sale():
    if request.method=='POST':
        orders, quantities, prices = (request.form.getlist(k) for k in ('order','quantity','price'))
        if not (0<len(orders)<=100 and len(orders)==len(quantities)==len(prices)):
            raise ValueError('Las líneas de venta están incompletas o exceden el límite de 100.')
        lines=list(zip(orders, quantities, prices))
        sale_id=services.sell(request.form.get('client'),lines,g.user['username'],g.user['id'],text('token'))
        flash('Venta registrada y stock actualizado.', 'success'); return redirect(url_for('sale_detail',sale_id=sale_id))
    stock=choices('''SELECT op.id,CONCAT(p.nombre,' · ',op.lote_producto_terminado,' · disponibles: ',s.cantidad_actual) label
        FROM kc_stock_terminado s JOIN ordenes_produccion op ON op.id=s.orden_id
        JOIN productos_terminados p ON p.id=op.producto_terminado_id WHERE s.cantidad_actual>0''')
    return render_template('operation.html',title='Nueva venta',operation='sale', options=stock,guide=sale_guide() if not stock else None,
        fields=[field('client','Cliente (opcional)','select',choices('SELECT id,nombre label FROM clientes ORDER BY nombre'),required=False)])


@app.get('/ventas/<int:sale_id>')
def sale_detail(sale_id):
    sale=one('SELECT v.*,c.nombre cliente FROM ventas v LEFT JOIN clientes c ON c.id=v.cliente_id WHERE v.id=%s',(sale_id,))
    if not sale: abort(404)
    data=rows('''SELECT d.*,p.nombre,op.lote_producto_terminado,a.cantidad asignada FROM detalle_ventas d
        JOIN productos_terminados p ON p.id=d.producto_terminado_id LEFT JOIN kc_asignaciones_venta a ON a.detalle_id=d.id
        LEFT JOIN ordenes_produccion op ON op.id=a.orden_id WHERE d.venta_id=%s''',(sale_id,))
    return render_template('sale.html',title=f'Venta #{sale_id}',sale=sale,data=data)


@app.route('/produccion/nueva',methods=['GET','POST'])
@permission('ALMACEN')
def production_new():
    error = None
    if request.method=='POST' and request.form.get('action')!='edit':
        sources, amounts = request.form.getlist('source'), request.form.getlist('amount')
        try:
            if not (0<len(sources)<=100 and len(sources)==len(amounts)):
                raise ValueError('Los consumos están incompletos o exceden el límite de 100.')
            product, lot, quantity, mode = text('product'), text('lot',50), text('quantity'), text('mode')
            consumed=list(zip(sources, amounts))
            if request.form.get('action')=='review':
                review=services.preview_production(product,quantity,consumed,mode)
                return render_template('production_review.html',title='Revisar producción',review=review,values=request.form)
            if request.form.get('action','confirm')!='confirm':
                abort(400)
            order_id=services.produce(product,lot,quantity,consumed,g.user['fullname'],request.form.get('notes',''),g.user['id'],text('token'),mode=mode)
            flash('Producción registrada: insumos descontados y unidades terminadas disponibles para vender.', 'success')
            return redirect(url_for('finished_inventory'))
        except ValueError as problem:
            error=str(problem)
    options=rows("""SELECT l.id,l.numero_lote,l.cantidad_actual,i.nombre,i.unidad_medida
        FROM lotes_insumo l JOIN items i ON i.id=l.item_id WHERE l.cantidad_actual>0 AND l.estado='DISPONIBLE'
        AND l.fecha_vencimiento>CURDATE() ORDER BY l.fecha_vencimiento,l.id""")
    guide=production_guide()
    source_ids=request.form.getlist('source') or ['']
    source_amounts=request.form.getlist('amount')
    source_rows=[(source,source_amounts[index] if index<len(source_amounts) else '') for index,source in enumerate(source_ids[:100])]
    return render_template('production_form.html',title='Registrar fabricación o envasado',options=options,
        guide=guide if guide['stage']!='production' else None,products=rows('SELECT * FROM productos_terminados ORDER BY nombre'),
        values=request.form,source_rows=source_rows,error=error), 400 if error else 200


@app.get('/produccion')
def production():
    data=rows('''SELECT op.*,p.nombre,s.cantidad_actual,d.modalidad FROM ordenes_produccion op JOIN productos_terminados p
        ON p.id=op.producto_terminado_id LEFT JOIN kc_stock_terminado s ON s.orden_id=op.id
        LEFT JOIN kc_production_details d ON d.orden_id=op.id ORDER BY op.id DESC''')
    return render_template('production.html',title='Producción',data=data,guide=production_guide())


@app.get('/productos/existencias')
def finished_inventory():
    q=request.args.get('q','').strip()
    data=rows('''SELECT op.id,op.lote_producto_terminado,op.fecha_produccion,p.codigo,p.nombre,
        p.volumen_contenido_litros,s.cantidad_actual,d.modalidad
        FROM kc_stock_terminado s JOIN ordenes_produccion op ON op.id=s.orden_id
        JOIN productos_terminados p ON p.id=op.producto_terminado_id
        LEFT JOIN kc_production_details d ON d.orden_id=op.id
        WHERE s.cantidad_actual>0 AND (p.nombre LIKE %s OR p.codigo LIKE %s OR op.lote_producto_terminado LIKE %s)
        ORDER BY p.nombre,op.fecha_produccion,op.id''',('%'+q+'%',)*3)
    return render_template('finished_inventory.html',title='Existencias de productos terminados',data=data,q=q)


@app.get('/trazabilidad')
def trace():
    q=request.args.get('q','').strip(); order=request.args.get('orden','')
    sql='''SELECT op.id orden_id,op.lote_producto_terminado,p.nombre producto,op.fecha_produccion,
        op.cantidad_producida,i.nombre insumo,c.sector,l.id lote_id,l.numero_lote,l.tanque_almacenamiento,
        tp.cantidad_descontada,i.unidad_medida FROM trazabilidad_produccion tp
        JOIN ordenes_produccion op ON op.id=tp.orden_produccion_id JOIN productos_terminados p ON p.id=op.producto_terminado_id
        JOIN lotes_insumo l ON l.id=tp.lote_insumo_id JOIN items i ON i.id=l.item_id JOIN categorias c ON c.id=i.categoria_id WHERE 1=1'''
    params=[]
    if q: sql+=' AND (op.lote_producto_terminado LIKE %s OR p.nombre LIKE %s OR l.numero_lote LIKE %s)'; params+=['%'+q+'%']*3
    if order: sql+=' AND op.id=%s'; params.append(int(order))
    start,end=request.args.get('desde',''),request.args.get('hasta','')
    if start: sql+=' AND op.fecha_produccion>=%s'; params.append(date.fromisoformat(start))
    if end: sql+=' AND op.fecha_produccion<%s'; params.append(date.fromisoformat(end)+timedelta(days=1))
    customers=rows('''SELECT v.id venta_id,v.fecha_venta,c.nombre cliente,a.cantidad FROM kc_asignaciones_venta a
        JOIN detalle_ventas d ON d.id=a.detalle_id JOIN ventas v ON v.id=d.venta_id LEFT JOIN clientes c ON c.id=v.cliente_id
        WHERE a.orden_id=%s ORDER BY v.id DESC''',(order,)) if order else []
    return render_template('trace.html',title='Trazabilidad',data=rows(sql+' ORDER BY op.fecha_produccion DESC,op.id DESC',params),q=q,order=order,customers=customers)


@app.get('/alertas')
def alerts():
    return render_template('alerts.html',title='Alertas y vencimientos',data=rows(ALERTS))


@app.get('/calendario')
def planner():
    month=request.args.get('mes') or now().strftime('%Y-%m')
    start=date.fromisoformat(month+'-01'); end=(start+timedelta(days=32)).replace(day=1)
    events=rows('SELECT * FROM kc_events WHERE starts_at<%s AND ends_at>=%s ORDER BY starts_at',(end,start))
    days=calendar.Calendar(firstweekday=0).monthdatescalendar(start.year,start.month)
    upcoming={}
    for week in days:
        for day in week:
            upcoming[day]=[x for x in events if x['starts_at'].date()<=day<=x['ends_at'].date()]
    return render_template('calendar.html',title='Calendario y recordatorios',month=month,start=start,days=days,events=events,byday=upcoming,
        previous=(start-timedelta(days=1)).strftime('%Y-%m'),following=end.strftime('%Y-%m'))


@app.route('/calendario/nuevo',methods=['GET','POST'])
@app.route('/calendario/<int:event_id>',methods=['GET','POST'])
def event(event_id=None):
    record=one('SELECT * FROM kc_events WHERE id=%s',(event_id,)) if event_id else None
    if event_id and not record: abort(404)
    if record and record['created_by']!=g.user['id'] and g.user['role']!='ADMIN':
        if request.method=='POST': abort(403)
        return render_template('event.html',title=record['title'],event=record)
    if request.method=='POST':
        starts=datetime.fromisoformat(text('starts_at')); ends=datetime.fromisoformat(text('ends_at'))
        if starts.tzinfo or ends.tzinfo or ends<starts: raise ValueError('El fin debe ser posterior o igual al inicio, en hora local.')
        status=text('status')
        if status not in ('PENDIENTE','COMPLETADA','CANCELADA'): raise ValueError('Estado inválido.')
        values=(text('title'),request.form.get('description',''),starts,ends,status)
        with transaction() as c:
            if event_id: c.execute('UPDATE kc_events SET title=%s,description=%s,starts_at=%s,ends_at=%s,status=%s WHERE id=%s',(*values,event_id))
            else: c.execute('INSERT INTO kc_events(title,description,starts_at,ends_at,status,created_by) VALUES(%s,%s,%s,%s,%s,%s)',(*values,g.user['id']))
        flash('Actividad guardada.', 'success'); return redirect(url_for('planner',mes=starts.strftime('%Y-%m')))
    default_start = now()
    if not record and request.args.get('dia'):
        default_start=datetime.combine(date.fromisoformat(request.args['dia']),datetime.min.time()).replace(hour=9)
    record=record or {}
    fields=[field('title','Actividad',value=record.get('title','')),field('description','Descripción',value=record.get('description',''),required=False),
        field('starts_at','Inicio','datetime-local',value=record.get('starts_at',default_start).strftime('%Y-%m-%dT%H:%M')),
        field('ends_at','Fin','datetime-local',value=record.get('ends_at',default_start+timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')),
        field('status','Estado','select',[(s,s.capitalize()) for s in ('PENDIENTE','COMPLETADA','CANCELADA')],value=record.get('status','PENDIENTE'))]
    return render_template('form.html',title='Editar actividad' if event_id else 'Nueva actividad',fields=fields,subtitle='Hora local de Bolivia · Las actividades se guardan en MySQL.')


@app.route('/configuracion',methods=['GET','POST'])
def settings():
    if request.method=='POST':
        if g.user['role']!='ADMIN': abort(403)
        password=text('password',200); role=text('role')
        if len(password)<12 or role not in ('ADMIN','ALMACEN','VENTAS'): raise ValueError('Contraseña de 12 caracteres como mínimo y rol válido requeridos.')
        with transaction() as c:
            c.execute('INSERT INTO kc_users(username,fullname,password_hash,role) VALUES(%s,%s,%s,%s)',
                      (text('username',80),text('fullname'),generate_password_hash(password),role))
        flash('Usuario creado.', 'success'); return redirect(url_for('settings'))
    return render_template('settings.html',title='Configuración',fields=[field('fullname','Nombre completo'),field('username','Usuario'),
        field('password','Contraseña (mínimo 12 caracteres)','password'),field('role','Rol','select',[(r,r) for r in ('ALMACEN','VENTAS','ADMIN')])],
        users=rows('SELECT username,fullname,role FROM kc_users ORDER BY id') if g.user['role']=='ADMIN' else [])


REPORTS={
 'inventario': 'SELECT * FROM v_inventario_peps',
 'ventas': 'SELECT id,fecha_venta,cliente_id,total_venta,usuario_registro FROM ventas ORDER BY fecha_venta DESC',
 'trazabilidad': 'SELECT * FROM v_trazabilidad_senasag'}


@app.get('/reportes')
def reports():
    return render_template('reports.html',title='Reportes')


@app.get('/reportes/<kind>.csv')
def report_csv(kind):
    if kind not in REPORTS: abort(404)
    with transaction() as c:
        c.execute(REPORTS[kind]); data=c.fetchall(); columns=[d[0] for d in c.description]
    output=io.StringIO(); writer=csv.writer(output,delimiter=';'); writer.writerow(columns)
    for row in data:
        values=[]
        for key in columns:
            value=row[key]
            if isinstance(value,str) and value.startswith(('=','+','-','@','\t','\r')): value="'"+value
            values.append(value)
        writer.writerow(values)
    return Response('\ufeff'+output.getvalue(),mimetype='text/csv',headers={'Content-Disposition':f'attachment; filename="king-cleaner-{kind}.csv"'})


if __name__=='__main__':
    from waitress import serve
    print('KING CLEANER · http://127.0.0.1:'+os.getenv('APP_PORT','5050'),flush=True)
    serve(app,host='127.0.0.1',port=int(os.getenv('APP_PORT','5050')),threads=4)
