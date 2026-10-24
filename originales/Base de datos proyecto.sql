DROP DATABASE IF EXISTS control_produccion_db;

CREATE DATABASE control_produccion_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE control_produccion_db;

CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    sector ENUM('GRANEL', 'UNIDADES') NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    categoria_id INT NOT NULL,
    unidad_medida ENUM('LITROS', 'UNIDADES') NOT NULL,
    stock_minimo DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lotes_insumo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    numero_lote VARCHAR(50) NOT NULL,
    cantidad_inicial DECIMAL(10,2) NOT NULL,
    cantidad_actual DECIMAL(10,2) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    tanque_almacenamiento VARCHAR(50) DEFAULT NULL,
    estado ENUM('DISPONIBLE', 'AGOTADO', 'VENCIDO') DEFAULT 'DISPONIBLE',
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uq_item_lote (item_id, numero_lote)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS productos_terminados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    volumen_contenido_litros DECIMAL(10,3) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ordenes_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lote_producto_terminado VARCHAR(50) NOT NULL UNIQUE,
    producto_terminado_id INT NOT NULL,
    fecha_produccion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cantidad_producida INT NOT NULL,
    responsable VARCHAR(100) NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (producto_terminado_id) REFERENCES productos_terminados(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS trazabilidad_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orden_produccion_id INT NOT NULL,
    lote_insumo_id INT NOT NULL,
    cantidad_descontada DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (orden_produccion_id) REFERENCES ordenes_produccion(id) ON DELETE CASCADE,
    FOREIGN KEY (lote_insumo_id) REFERENCES lotes_insumo(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW v_alertas_vencimiento AS
SELECT 
    l.id AS lote_id,
    i.codigo,
    i.nombre AS material,
    c.sector,
    l.numero_lote,
    l.cantidad_actual,
    i.unidad_medida,
    l.fecha_vencimiento,
    DATEDIFF(l.fecha_vencimiento, CURDATE()) AS dias_para_vencer,
    CASE 
        WHEN DATEDIFF(l.fecha_vencimiento, CURDATE()) <= 0 THEN 'CRITICO_VENCIDO'
        WHEN DATEDIFF(l.fecha_vencimiento, CURDATE()) <= 7 THEN 'CRITICO_7_DIAS'
        WHEN DATEDIFF(l.fecha_vencimiento, CURDATE()) <= 30 THEN 'ADVERTENCIA_30_DIAS'
        ELSE 'NORMAL'
    END AS estado_alerta
FROM lotes_insumo l
JOIN items i ON l.item_id = i.id
JOIN categorias c ON i.categoria_id = c.id
WHERE l.cantidad_actual > 0 AND l.estado = 'DISPONIBLE'
ORDER BY l.fecha_vencimiento ASC;

CREATE OR REPLACE VIEW v_inventario_peps AS
SELECT 
    i.id AS item_id,
    i.codigo,
    i.nombre AS material,
    c.sector,
    l.id AS lote_id,
    l.numero_lote,
    l.cantidad_actual,
    i.unidad_medida,
    l.fecha_vencimiento,
    l.tanque_almacenamiento
FROM lotes_insumo l
JOIN items i ON l.item_id = i.id
JOIN categorias c ON i.categoria_id = c.id
WHERE l.cantidad_actual > 0 AND l.estado = 'DISPONIBLE'
ORDER BY i.id ASC, l.fecha_vencimiento ASC, l.fecha_ingreso ASC;

CREATE OR REPLACE VIEW v_trazabilidad_senasag AS
SELECT 
    op.lote_producto_terminado AS lote_producto_final,
    pt.nombre AS producto,
    op.fecha_produccion,
    op.cantidad_producida AS unidades_envasadas,
    i.nombre AS insumo_utilizado,
    c.sector AS tipo_insumo,
    li.numero_lote AS lote_origen_insumo,
    li.tanque_almacenamiento AS tanque_origen,
    tp.cantidad_descontada
FROM ordenes_produccion op
JOIN productos_terminados pt ON op.producto_terminado_id = pt.id
JOIN trazabilidad_produccion tp ON op.id = tp.orden_produccion_id
JOIN lotes_insumo li ON tp.lote_insumo_id = li.id
JOIN items i ON li.item_id = i.id
JOIN categorias c ON i.categoria_id = c.id
ORDER BY op.fecha_produccion DESC;

INSERT INTO categorias (nombre, sector) VALUES 
('Líquidos y Químicos', 'GRANEL'),
('Envases y Plásticos', 'UNIDADES'),
('Etiquetas y Embalaje', 'UNIDADES');

INSERT INTO items (codigo, nombre, categoria_id, unidad_medida) VALUES 
('MP-001', 'Hipoclorito de Sodio', 1, 'LITROS'),
('MP-002', 'Fragancia Lavanda', 1, 'LITROS'),
('INS-001', 'Envase Plástico 1L', 2, 'UNIDADES'),
('INS-002', 'Tapa Rosca Azul', 2, 'UNIDADES');

INSERT INTO lotes_insumo (item_id, numero_lote, cantidad_inicial, cantidad_actual, fecha_ingreso, fecha_vencimiento, tanque_almacenamiento) VALUES 
(1, 'L-HIPO-01', 1000.00, 1000.00, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'Tanque A-1'),
(1, 'L-HIPO-02', 1000.00, 1000.00, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 45 DAY), 'Tanque A-2'),
(2, 'L-FRAG-01', 200.00, 200.00, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 20 DAY), 'Tanque B-1'),
(3, 'L-ENV-100', 5000.00, 5000.00, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 730 DAY), NULL),
(4, 'L-TAP-100', 5000.00, 5000.00, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 730 DAY), NULL);
-- TABLA DE CLIENTES
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    nit_ci VARCHAR(50) DEFAULT NULL,
    telefono VARCHAR(30) DEFAULT NULL,
    direccion TEXT DEFAULT NULL
) ENGINE=InnoDB;

-- TABLA CABECERA DE VENTAS
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT DEFAULT NULL,
    fecha_venta DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_venta DECIMAL(10,2) NOT NULL,
    usuario_registro VARCHAR(100) NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- TABLA DETALLE DE VENTAS (Qué productos y qué cantidad se vendió)
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_terminado_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_terminado_id) REFERENCES productos_terminados(id) ON DELETE RESTRICT
) ENGINE=InnoDB;