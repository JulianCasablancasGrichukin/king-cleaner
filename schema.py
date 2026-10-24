"""Install the supplied schema without DROP, USE or sample INSERT statements."""
from pathlib import Path
import re
from db import transaction

EXTRA = '''
CREATE TABLE IF NOT EXISTS kc_migrations (version INT PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS kc_users (
 id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(80) NOT NULL UNIQUE,
 fullname VARCHAR(150) NOT NULL, password_hash VARCHAR(255) NOT NULL,
 role ENUM('ADMIN','ALMACEN','VENTAS') NOT NULL DEFAULT 'ALMACEN');
CREATE TABLE IF NOT EXISTS kc_events (
 id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(150) NOT NULL, description TEXT,
 starts_at DATETIME NOT NULL, ends_at DATETIME NOT NULL,
 status ENUM('PENDIENTE','COMPLETADA','CANCELADA') NOT NULL DEFAULT 'PENDIENTE',
 created_by INT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY(created_by) REFERENCES kc_users(id));
CREATE TABLE IF NOT EXISTS kc_movimientos (
 id INT AUTO_INCREMENT PRIMARY KEY, lote_id INT NOT NULL, delta DECIMAL(10,2) NOT NULL,
 motivo VARCHAR(250) NOT NULL, usuario_id INT NOT NULL,
 fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(lote_id) REFERENCES lotes_insumo(id), FOREIGN KEY(usuario_id) REFERENCES kc_users(id));
CREATE TABLE IF NOT EXISTS kc_stock_terminado (
 orden_id INT PRIMARY KEY, cantidad_actual INT NOT NULL,
 FOREIGN KEY(orden_id) REFERENCES ordenes_produccion(id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS kc_asignaciones_venta (
 id INT AUTO_INCREMENT PRIMARY KEY, detalle_id INT NOT NULL, orden_id INT NOT NULL,
 cantidad INT NOT NULL, FOREIGN KEY(detalle_id) REFERENCES detalle_ventas(id) ON DELETE RESTRICT,
 FOREIGN KEY(orden_id) REFERENCES ordenes_produccion(id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS kc_requests (
 token VARCHAR(64) PRIMARY KEY, usuario_id INT NOT NULL,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
'''


def original_statements():
    text = (Path(__file__).parent / 'originales' / 'Base de datos proyecto.sql').read_text(encoding='utf-8-sig')
    text = re.sub(r'--[^\n]*', '', text)
    return [s.strip() for s in text.split(';') if s.strip().upper().startswith(('CREATE TABLE', 'CREATE OR REPLACE VIEW'))]


def install(new=False):
    with transaction() as c:
        c.execute('SHOW TABLES')
        existing = c.fetchall()
        if new and existing:
            raise ValueError('La base contiene objetos. No se permite inicializarla como nueva.')
        if new:
            for statement in original_statements():
                c.execute(statement)
        else:
            # Existing migrations never replace the original views/tables.
            c.execute('SELECT id FROM detalle_ventas LIMIT 0')
            c.execute('SELECT id FROM trazabilidad_produccion LIMIT 0')
        for statement in EXTRA.split(';'):
            if statement.strip():
                c.execute(statement)
        c.execute('INSERT IGNORE INTO kc_migrations(version) VALUES (1)')
