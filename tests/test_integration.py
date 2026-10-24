"""Real MySQL integration checks. Set KC_TEST_ADMIN_FILE to a local admin JSON.
Creates a uniquely named test database; never uses control_produccion_db.
"""
import json
import os
import secrets
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import pymysql

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope='session',autouse=True)
def database():
    config_path=os.getenv('KC_TEST_ADMIN_FILE')
    if not config_path: pytest.skip('KC_TEST_ADMIN_FILE necesario para MySQL real')
    config=json.loads(Path(config_path).read_text())
    name='king_cleaner_test_'+secrets.token_hex(5)
    os.environ.update(DB_HOST='127.0.0.1',DB_PORT=str(config['port']),DB_USER=config['user'],DB_PASSWORD=config['password'],DB_NAME=name)
    from db import connect
    conn=connect(False)
    with conn.cursor() as c: c.execute(f'CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    conn.commit();conn.close()
    from schema import install
    install(new=True)
    yield name
    # Keep the isolated database available for audit; never clean up a user database.


@pytest.fixture(autouse=True)
def clear_test_data(database):
    from db import transaction
    assert os.environ['DB_NAME']==database and database.startswith('king_cleaner_test_')
    with transaction() as c:
        for table in ['kc_asignaciones_venta','detalle_ventas','ventas','kc_stock_terminado','trazabilidad_produccion','ordenes_produccion','kc_movimientos','lotes_insumo','items','categorias','productos_terminados','clientes','kc_events','kc_requests','kc_users']:
            c.execute(f'DELETE FROM {table}')


@pytest.fixture
def app():
    from app import app
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def client(app):
    from db import transaction
    from werkzeug.security import generate_password_hash
    with transaction() as c:
        c.execute("INSERT INTO kc_users(username,fullname,password_hash,role) VALUES('tester','Pruebas aisladas',%s,'ADMIN')",(generate_password_hash('integration-password'),))
        user=c.lastrowid
    client=app.test_client()
    with client.session_transaction() as s: s.update(user_id=user,csrf='test-csrf')
    client.test_user=user
    return client


@pytest.fixture
def stock(client):
    from db import transaction
    from services import receive,today
    with transaction() as c:
        c.execute("INSERT INTO categorias(nombre,sector) VALUES('TEST químicos','GRANEL')"); category=c.lastrowid
        c.execute("INSERT INTO items(codigo,nombre,categoria_id,unidad_medida) VALUES('TEST-MP','TEST material',%s,'LITROS')",(category,)); item=c.lastrowid
        c.execute("INSERT INTO productos_terminados(codigo,nombre,volumen_contenido_litros) VALUES('TEST-PT','TEST producto',1)"); product=c.lastrowid
    receive(item,'TEST-LOTE',100,today().isoformat(),(today()+timedelta(days=5)).isoformat(),'TEST tanque',client.test_user,secrets.token_hex(32))
    from db import one
    lot=one('SELECT id FROM lotes_insumo')['id']
    return dict(item=item,lot=lot,product=product,user=client.test_user)


def production(stock,qty=10,amount=10):
    from services import produce
    return produce(stock['product'],'TEST-FINAL-'+secrets.token_hex(3),qty,[(stock['lot'],amount)],'TEST responsable','',stock['user'],secrets.token_hex(32))


def test_empty_database_routes(client):
    routes=['/','/inventario','/inventario?sector=UNIDADES','/ventas','/ventas?modo=mensual','/ventas?modo=anual','/ventas/nueva','/produccion','/produccion/nueva','/trazabilidad','/alertas','/calendario','/calendario/nuevo','/recepcion','/catalogos/categorias','/catalogos/materiales','/catalogos/productos','/catalogos/clientes','/configuracion','/reportes','/reportes/ventas.csv']
    for route in routes:
        result=client.get(route)
        assert result.status_code==200,(route,result.data.decode())


def test_full_production_sale_trace(stock,client):
    from services import sell
    from db import one
    order=production(stock,10,7.25)
    sale=sell(None,[(order,2,'12.50'),(order,1,'13.25')],'tester',stock['user'],secrets.token_hex(32))
    assert one('SELECT total_venta FROM ventas WHERE id=%s',(sale,))['total_venta']==Decimal('38.25')
    assert one('SELECT cantidad_actual FROM lotes_insumo WHERE id=%s',(stock['lot'],))['cantidad_actual']==Decimal('92.75')
    assert one('SELECT cantidad_actual FROM kc_stock_terminado WHERE orden_id=%s',(order,))['cantidad_actual']==7
    assert len(__import__('db').rows('SELECT * FROM kc_asignaciones_venta'))==2
    for route in [f'/ventas/{sale}',f'/trazabilidad?orden={order}',f'/lotes/{stock["lot"]}','/produccion','/ventas','/']:
        assert client.get(route).status_code==200
    assert b'38,25' in client.get('/ventas').data


def test_production_rollback(stock):
    from db import one
    with pytest.raises(ValueError): production(stock,10,101)
    assert one('SELECT COUNT(*) n FROM ordenes_produccion')['n']==0
    assert one('SELECT cantidad_actual FROM lotes_insumo')['cantidad_actual']==100
    assert one('SELECT COUNT(*) n FROM trazabilidad_produccion')['n']==0


def test_sale_rollback_and_replay(stock):
    from services import sell
    from db import one
    order=production(stock,3,1)
    with pytest.raises(ValueError): sell(None,[(order,2,5),(order,2,5)],'tester',stock['user'],secrets.token_hex(32))
    assert one('SELECT COUNT(*) n FROM ventas')['n']==0
    assert one('SELECT cantidad_actual FROM kc_stock_terminado')['cantidad_actual']==3
    token=secrets.token_hex(32)
    sell(None,[(order,1,5)],'tester',stock['user'],token)
    with pytest.raises(pymysql.IntegrityError): sell(None,[(order,1,5)],'tester',stock['user'],token)
    assert one('SELECT COUNT(*) n FROM ventas')['n']==1


def test_concurrent_sales_do_not_oversell(stock):
    from services import sell
    from db import one
    order=production(stock,5,1)
    def attempt(_):
        try:
            sell(None,[(order,4,2)],'tester',stock['user'],secrets.token_hex(32)); return True
        except ValueError: return False
    with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(attempt,range(2)))
    assert sum(results)==1
    assert one('SELECT cantidad_actual FROM kc_stock_terminado')['cantidad_actual']==1


def test_alert_boundaries(stock,client):
    from db import transaction,rows
    from services import today
    from app import ALERTS
    with transaction() as c:
        c.execute('DELETE FROM kc_movimientos');c.execute('DELETE FROM lotes_insumo')
        for days in [0,7,8,30,31]:
            c.execute('''INSERT INTO lotes_insumo(item_id,numero_lote,cantidad_inicial,cantidad_actual,fecha_ingreso,fecha_vencimiento)
                VALUES(%s,%s,1,1,%s,%s)''',(stock['item'],str(days),today(),today()+timedelta(days=days)))
        c.execute("UPDATE lotes_insumo SET estado='VENCIDO' WHERE numero_lote='0'")
    data={r['numero_lote']:r['gravedad'] for r in rows(ALERTS)}
    assert data=={'0':'Vencido','7':'Crítico','8':'Atención','30':'Atención'}
    assert client.get('/alertas').status_code==200


def test_expired_rejected(stock):
    from db import transaction,one
    with transaction() as c: c.execute('UPDATE lotes_insumo SET fecha_vencimiento=CURDATE()')
    with pytest.raises(ValueError): production(stock)
    assert one('SELECT cantidad_actual FROM lotes_insumo')['cantidad_actual']==100


def test_adjustment_audit(stock):
    from services import adjust
    from db import one
    adjust(stock['lot'],90,'Conteo físico verificado',stock['user'],secrets.token_hex(32))
    assert one('SELECT delta FROM kc_movimientos ORDER BY id DESC LIMIT 1')['delta']==-10
    with pytest.raises(ValueError): adjust(stock['lot'],-1,'Inválido',stock['user'],secrets.token_hex(32))
    assert one('SELECT cantidad_actual FROM lotes_insumo')['cantidad_actual']==90


def test_calendar_persistence(client):
    from db import one
    result=client.post('/calendario/nuevo',data=dict(csrf='test-csrf',title='TEST actividad',description='Solo prueba',starts_at='2026-12-31T23:00',ends_at='2027-01-01T01:00',status='PENDIENTE'))
    assert result.status_code==302
    event=one('SELECT * FROM kc_events')
    assert b'TEST actividad' in client.get('/calendario?mes=2027-01').data
    assert client.post(f'/calendario/{event["id"]}',data=dict(csrf='test-csrf',title='TEST actividad',description='',starts_at='2026-12-31T23:00',ends_at='2027-01-01T01:00',status='COMPLETADA')).status_code==302
    assert one('SELECT status FROM kc_events')['status']=='COMPLETADA'
    bad=client.post('/calendario/nuevo',data=dict(csrf='test-csrf',title='TEST inválida',starts_at='2026-12-31T23:00',ends_at='2026-01-01T01:00',status='PENDIENTE'))
    assert bad.status_code==400
    assert one('SELECT COUNT(*) n FROM kc_events')['n']==1


def test_auth_permissions_and_csrf(client):
    from db import transaction
    assert client.post('/salir',data={}).status_code==400
    with transaction() as c: c.execute("UPDATE kc_users SET role='VENTAS'")
    assert client.get('/recepcion').status_code==403
    assert client.post('/configuracion',data={'csrf':'test-csrf'}).status_code==403
    assert client.post('/salir',data={'csrf':'test-csrf'}).status_code==302
    assert client.get('/inventario').status_code==302
    client.get('/acceso')
    with client.session_transaction() as s: csrf=s['csrf']
    assert b'incorrectos' in client.post('/acceso',data=dict(csrf=csrf,username='tester',password='incorrect')).data
    assert client.post('/acceso',data=dict(csrf=csrf,username='tester',password='integration-password')).status_code==302


def test_initial_admin(app):
    from db import one
    client=app.test_client()
    assert client.get('/primer-acceso').status_code==200
    with client.session_transaction() as s: csrf=s['csrf']
    assert client.post('/primer-acceso',data=dict(csrf=csrf,username='first',fullname='TEST first',password='long-test-password',confirm='long-test-password')).status_code==302
    assert one('SELECT COUNT(*) n FROM kc_users')['n']==1
    assert client.get('/primer-acceso').status_code==302


def test_migration_preserves_existing(stock):
    from schema import install
    from db import one
    before=one('SELECT * FROM lotes_insumo')
    install(new=False);install(new=False)
    assert one('SELECT * FROM lotes_insumo')==before
    with pytest.raises(ValueError): install(new=True)


def test_decimal_and_whole_validation():
    from services import number
    for value in ['NaN','Infinity','-1','0','0.001']:
        with pytest.raises(ValueError): number(value)
    with pytest.raises(ValueError): number('1.5',whole=True)
    assert number('12.30')==Decimal('12.30')


def test_database_failure_is_not_empty_state(client,monkeypatch):
    monkeypatch.setenv('DB_PORT','1')
    response=client.get('/inventario')
    assert response.status_code==503
    assert 'Base de datos no disponible' in response.data.decode()


def test_csv_injection_protection(client):
    from db import transaction
    with transaction() as c: c.execute("INSERT INTO ventas(total_venta,usuario_registro) VALUES(1,'=TEST()')")
    response=client.get('/reportes/ventas.csv')
    assert "'=TEST()" in response.data.decode()


def test_web_forms_complete_cycle(client):
    from db import one
    from services import today
    def post(url,**data):
        return client.post(url,data=dict(csrf='test-csrf',token=secrets.token_hex(32),**data))
    assert post('/catalogos/categorias',nombre='TEST categoría',sector='GRANEL',descripcion='').status_code==302
    category=one('SELECT id FROM categorias')['id']
    assert post('/catalogos/materiales',codigo='TEST-MAT',nombre='TEST materia',categoria_id=category,unidad_medida='LITROS',stock_minimo=1).status_code==302
    item=one('SELECT id FROM items')['id']
    assert post('/catalogos/productos',codigo='TEST-PROD',nombre='TEST frasco',volumen_contenido_litros='0.125').status_code==302
    product=one('SELECT id FROM productos_terminados')['id']
    assert post('/recepcion',item=item,lot='TEST-REC',quantity=50,entered=str(today()),expires=str(today()+timedelta(days=90)),tank='').status_code==302
    lot=one('SELECT id FROM lotes_insumo')['id']
    assert post('/produccion/nueva',product=product,lot='TEST-FINAL',quantity=10,source=str(lot),amount='1.25',notes='').status_code==302
    order=one('SELECT id FROM ordenes_produccion')['id']
    assert post('/ventas/nueva',client='',order=str(order),quantity='2',price='5.20').status_code==302
    assert one('SELECT total_venta FROM ventas')['total_venta']==Decimal('10.40')
    assert post('/ventas/nueva',client='',order=str(order),quantity='2').status_code==400


def test_calendar_read_only_other_user(client):
    from db import transaction,one
    from werkzeug.security import generate_password_hash
    with transaction() as c:
        c.execute("INSERT INTO kc_users(username,fullname,password_hash,role) VALUES('other','TEST other',%s,'VENTAS')",(generate_password_hash('another-password'),))
        other=c.lastrowid
        c.execute("INSERT INTO kc_events(title,starts_at,ends_at,created_by) VALUES('TEST compartida',NOW(),NOW(),%s)",(client.test_user,))
        event=c.lastrowid
    with client.session_transaction() as s: s['user_id']=other
    assert client.get(f'/calendario/{event}').status_code==200
    assert client.post(f'/calendario/{event}',data={'csrf':'test-csrf'}).status_code==403


def test_day_selection_prefills_event(client):
    response=client.get('/calendario/nuevo?dia=2027-02-03')
    assert b'2027-02-03T09:00' in response.data
    assert b'2027-02-03T10:00' in response.data
