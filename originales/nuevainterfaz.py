import sys
import math
from BDconexion import DatabaseManager
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QStackedWidget, QScrollArea, QFrame, QMessageBox,
    QComboBox, QProgressBar
)

COLOR_BG = "#FCFCF4"       
COLOR_NAVY = "#020378"  
COLOR_BLUE_LIGHT = "#0284C7"   
COLOR_GOLD = "#FFBB33"     
COLOR_ORANGE = "#FF6B00"    
COLOR_TEXT_DARK = "#0F172A"
COLOR_TEXT_MUTED = "#475569"
COLOR_CARD_BG = "#FFFFFF"

class KingCleanerLogoWidget(QWidget):
    def __init__(self, size=115, parent=None):
        super().__init__(parent)
        self.size_px = size
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2.0, h / 2.0
        radius = (w / 2.0) - 14

        # Círculo Blanco Exterior
        rect = QRectF(3, 3, w - 6, h - 6)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor(COLOR_NAVY), 3.5))
        painter.drawEllipse(rect)

        # Círculo Interior Punteado
        inner_rect = QRectF(10, 10, w - 20, h - 20)
        painter.setPen(QPen(QColor(COLOR_NAVY), 1.5, Qt.PenStyle.DashLine))
        painter.drawEllipse(inner_rect)

        # Texto Central "KC"
        painter.setFont(QFont("Segoe UI", int(self.size_px * 0.28), QFont.Weight.Bold))
        painter.setPen(QPen(QColor(COLOR_NAVY)))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "KC")

        # TEXTO CURVO SUPERIOR ("KING CLEANER") ---
        text_top = "KING CLEANER"
        font_top = QFont("Segoe UI", int(self.size_px * 0.08), QFont.Weight.Bold)
        painter.setFont(font_top)
        painter.setPen(QPen(QColor(COLOR_NAVY)))

        angle_per_char = 9.5 
        start_angle = - (len(text_top) - 1) * angle_per_char / 2.0

        for i, char in enumerate(text_top):
            angle_deg = start_angle + (i * angle_per_char)
            angle_rad = math.radians(angle_deg - 90) 
            
            x = cx + radius * math.cos(angle_rad)
            y = cy + radius * math.sin(angle_rad)

            painter.save()
            painter.translate(x, y)
            painter.rotate(angle_deg) 
            painter.drawText(QRectF(-10, -10, 20, 20), Qt.AlignmentFlag.AlignCenter, char)
            painter.restore()

        # --- TEXTO CURVO INFERIOR ("LIDER LIMPIADOR") ---
        text_bot = "LIDER LIMPIADOR"
        font_bot = QFont("Segoe UI", int(self.size_px * 0.07), QFont.Weight.Bold)
        painter.setFont(font_bot)
        painter.setPen(QPen(QColor(COLOR_ORANGE)))

        angle_per_char_bot = 8.5
        start_angle_bot = - (len(text_bot) - 1) * angle_per_char_bot / 2.0

        for i, char in enumerate(text_bot):
            angle_deg = start_angle_bot + (i * angle_per_char_bot)
            angle_rad = math.radians(angle_deg + 90)
            
            x = cx + radius * math.cos(angle_rad)
            y = cy + radius * math.sin(angle_rad)

            painter.save()
            painter.translate(x, y)
            painter.rotate(-angle_deg)
            painter.drawText(QRectF(-10, -10, 20, 20), Qt.AlignmentFlag.AlignCenter, char)
            painter.restore()

# COMPONENTES REUTILIZABLES LIMPIOS
class ModernCard(QFrame):
    def __init__(self, parent=None, bg_color=COLOR_CARD_BG, border_color="#E2E8F0", radius=12):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {radius}px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

class StatCard(QFrame):
    def __init__(self, icon_str, title, value_str, subtext):
        super().__init__()
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {COLOR_CARD_BG};
                border: 1px solid {COLOR_NAVY};
                border-radius: 12px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        icon_box = QLabel(icon_str)
        icon_box.setFixedSize(40, 40)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        icon_box.setStyleSheet(f"background-color: #EEF2FF; color: {COLOR_NAVY}; border-radius: 20px;")
        layout.addWidget(icon_box)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: bold;")
        
        lbl_value = QLabel(value_str)
        lbl_value.setStyleSheet(f"color: {COLOR_NAVY}; font-size: 16px; font-weight: bold;")
        
        lbl_sub = QLabel(subtext)
        lbl_sub.setStyleSheet("color: #059669; font-size: 10px; font-weight: 500;")

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)
        text_layout.addWidget(lbl_sub)
        
        layout.addLayout(text_layout)

# PANTALLA LOGIN
class LoginWindow(QWidget):
    def __init__(self, on_login_success, on_go_to_register):
        super().__init__()
        self.on_login_success = on_login_success
        self.on_go_to_register = on_go_to_register
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = ModernCard(bg_color=COLOR_CARD_BG, border_color=COLOR_NAVY, radius=16)
        card.setFixedSize(380, 500)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(12)

        logo_container = QHBoxLayout()
        logo_container.addStretch()
        logo_container.addWidget(KingCleanerLogoWidget(size=85))
        logo_container.addStretch()
        card_layout.addLayout(logo_container)

        lbl_title = QLabel("👑 KING CLEANER")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {COLOR_NAVY}; margin-top: 4px;")

        lbl_sub = QLabel("Acceso al Sistema de Control e Inventario")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px;")

        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_sub)
        card_layout.addSpacing(6)

        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Nombre de usuario")
        self.style_input(self.txt_user)

        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Contraseña")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.style_input(self.txt_pass)

        card_layout.addWidget(QLabel("Usuario:", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold; font-size: 12px;"))
        card_layout.addWidget(self.txt_user)
        card_layout.addWidget(QLabel("Contraseña:", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold; font-size: 12px;"))
        card_layout.addWidget(self.txt_pass)
        card_layout.addSpacing(10)

        btn_login = QPushButton("Iniciar Sesión")
        btn_login.setFixedHeight(40)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_GOLD}; color: {COLOR_NAVY};
                font-weight: bold; font-size: 13px; border-radius: 8px; border: none;
            }}
            QPushButton:hover {{ background-color: #E6A82E; }}
        """)
        btn_login.clicked.connect(lambda: self.on_login_success(self.txt_user.text() or "Administrador"))
        card_layout.addWidget(btn_login)

        btn_register = QPushButton("¿No tienes cuenta? Regístrate aquí")
        btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_register.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {COLOR_NAVY};
                font-size: 11px; text-decoration: underline; border: none;
            }}
            QPushButton:hover {{ color: {COLOR_ORANGE}; }}
        """)
        btn_register.clicked.connect(self.on_go_to_register)
        card_layout.addWidget(btn_register)

        main_layout.addWidget(card)

    def style_input(self, widget):
        widget.setFixedHeight(36)
        widget.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #CBD5E1; border-radius: 8px; padding: 0 10px;
                background-color: #F8FAFC; color: {COLOR_TEXT_DARK};
            }}
            QLineEdit:focus {{ border: 2px solid {COLOR_NAVY}; background-color: #FFFFFF; }}
        """)

# PANTALLA REGISTRO
class RegisterWindow(QWidget):
    def __init__(self, on_back_to_login):
        super().__init__()
        self.on_back_to_login = on_back_to_login
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = ModernCard(bg_color=COLOR_CARD_BG, border_color=COLOR_NAVY, radius=16)
        card.setFixedSize(400, 540)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 24, 32, 24)
        card_layout.setSpacing(10)

        lbl_title = QLabel("📝 Registro de Usuario")
        lbl_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {COLOR_NAVY};")
        card_layout.addWidget(lbl_title)

        self.txt_fullname = QLineEdit()
        self.txt_fullname.setPlaceholderText("Nombre Completo")
        self.style_input(self.txt_fullname)

        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Nombre de Usuario")
        self.style_input(self.txt_user)

        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["Operario de Almacén", "Administrador de Planta", "Encargado de Ventas"])
        self.cmb_role.setFixedHeight(36)
        self.cmb_role.setStyleSheet(f"border: 1px solid #CBD5E1; border-radius: 8px; padding: 0 8px; color: {COLOR_TEXT_DARK};")

        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Contraseña")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.style_input(self.txt_pass)

        self.txt_pass_confirm = QLineEdit()
        self.txt_pass_confirm.setPlaceholderText("Confirmar Contraseña")
        self.txt_pass_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.style_input(self.txt_pass_confirm)

        card_layout.addWidget(QLabel("Nombre Completo:", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold;"))
        card_layout.addWidget(self.txt_fullname)
        card_layout.addWidget(QLabel("Usuario:", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold;"))
        card_layout.addWidget(self.txt_user)
        card_layout.addWidget(QLabel("Rol de Usuario:", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold;"))
        card_layout.addWidget(self.cmb_role)
        card_layout.addWidget(QLabel("Contraseña:", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold;"))
        card_layout.addWidget(self.txt_pass)
        card_layout.addWidget(QLabel("Confirmar Contraseña:", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold;"))
        card_layout.addWidget(self.txt_pass_confirm)
        card_layout.addSpacing(8)

        btn_save = QPushButton("Crear Cuenta")
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_GOLD}; color: {COLOR_NAVY};
                font-weight: bold; font-size: 13px; border-radius: 8px; border: none;
            }}
            QPushButton:hover {{ background-color: #E6A82E; }}
        """)
        btn_save.clicked.connect(self.handle_register)
        card_layout.addWidget(btn_save)

        btn_back = QPushButton("← Volver al Iniciar Sesión")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"background-color: transparent; color: {COLOR_NAVY}; border: none;")
        btn_back.clicked.connect(self.on_back_to_login)
        card_layout.addWidget(btn_back)

        main_layout.addWidget(card)

    def style_input(self, widget):
        widget.setFixedHeight(34)
        widget.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #CBD5E1; border-radius: 8px; padding: 0 10px;
                background-color: #F8FAFC; color: {COLOR_TEXT_DARK};
            }}
            QLineEdit:focus {{ border: 2px solid {COLOR_NAVY}; background-color: #FFFFFF; }}
        """)

    def handle_register(self):
        QMessageBox.information(self, "Registro Exitoso", "El usuario ha sido registrado correctamente.")
        self.on_back_to_login()

# INICIO 
class HomeDashboardView(QWidget):
    def __init__(self, switch_view_callback):
        super().__init__()
        self.switch_view_callback = switch_view_callback
        self.db = DatabaseManager()  # Conexión a la base de datos
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self.init_ui()

    def init_ui(self):
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(16, 16, 16, 16)
        master_layout.setSpacing(16)

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        # Banner Bienvenida
        banner = ModernCard(bg_color="#E0F2FE", border_color="#BAE6FD", radius=16)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(20, 16, 20, 16)

        b_text_layout = QVBoxLayout()
        lbl_welcome = QLabel("¡Bienvenido a King Cleaner!")
        lbl_welcome.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_welcome.setStyleSheet(f"color: {COLOR_NAVY};")
        lbl_slogan = QLabel("Tu aliado en limpieza, control y crecimiento.")
        lbl_slogan.setStyleSheet("color: #0284C7; font-size: 12px;")
        b_text_layout.addWidget(lbl_welcome)
        b_text_layout.addWidget(lbl_slogan)

        lbl_quality = QLabel("✨ Calidad que se nota ♡")
        lbl_quality.setStyleSheet("color: #0284C7; font-size: 12px; font-weight: bold;")
        banner_layout.addLayout(b_text_layout)
        banner_layout.addStretch()
        banner_layout.addWidget(lbl_quality)
        left_layout.addWidget(banner)

        # KPIs Superiores
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)
        kpi_layout.addWidget(StatCard("🛒", "Ventas de hoy", "Bs. 0,00", "Sin registros"))
        kpi_layout.addWidget(StatCard("📦", "Productos en stock", "Activo", "Base de datos conectada"))
        kpi_layout.addWidget(StatCard("⚙️", "Producción de hoy", "0 L", "En espera"))
        kpi_layout.addWidget(StatCard("⚠️", "Alertas activas", "0", "Todo en orden"))
        left_layout.addLayout(kpi_layout)

        # Gráfico y Top Productos
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(12)

        sales_card = ModernCard(border_color=COLOR_NAVY)
        sales_vbox = QVBoxLayout(sales_card)
        sales_vbox.setContentsMargins(14, 14, 14, 14)

        sales_header = QHBoxLayout()
        lbl_sales_title = QLabel("📊 Ventas")
        lbl_sales_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_NAVY};")
        sales_header.addWidget(lbl_sales_title)
        sales_header.addStretch()

        for btn_text in ["Diario", "Mensual", "Anual"]:
            b = QPushButton(btn_text)
            b.setFixedHeight(26)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if btn_text == "Diario":
                b.setStyleSheet(f"background-color: {COLOR_NAVY}; color: white; padding: 0 10px; border-radius: 6px; font-size: 11px; font-weight: bold;")
                b.clicked.connect(lambda: self.switch_view_callback("ventas_diario"))
            else:
                b.setStyleSheet("background-color: #F1F5F9; color: #64748B; padding: 0 10px; border-radius: 6px; font-size: 11px;")
            sales_header.addWidget(b)
        sales_vbox.addLayout(sales_header)

        for day in ["Lun 02", "Mar 03", "Mié 04", "Jue 05", "Vie 06", "Sáb 07", "Dom 08"]:
            row_day = QHBoxLayout()
            lbl_d = QLabel(day)
            lbl_d.setFixedWidth(50)
            lbl_d.setStyleSheet("color: #64748B; font-size: 11px;")
            
            pbar = QProgressBar()
            pbar.setValue(0)
            pbar.setMaximum(100)
            pbar.setFixedHeight(10)
            pbar.setStyleSheet(f"QProgressBar {{ border: 1px solid #CBD5E1; border-radius: 5px; background-color: #F8FAFC; }} QProgressBar::chunk {{ background-color: {COLOR_NAVY}; border-radius: 4px; }}")
            lbl_val = QLabel("Bs. 0,00")
            lbl_val.setStyleSheet(f"color: {COLOR_TEXT_DARK}; font-size: 11px; font-weight: bold;")
            
            row_day.addWidget(lbl_d)
            row_day.addWidget(pbar)
            row_day.addWidget(lbl_val)
            sales_vbox.addLayout(row_day)

        sales_vbox.addStretch()
        mid_layout.addWidget(sales_card, stretch=2)

        # Productos más vendidos
        top_card = ModernCard(border_color=COLOR_NAVY)
        top_vbox = QVBoxLayout(top_card)
        top_vbox.setContentsMargins(14, 14, 14, 14)

        lbl_top_title = QLabel("🏆 Productos más vendidos")
        lbl_top_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_NAVY};")
        top_vbox.addWidget(lbl_top_title)

        top_vbox.addWidget(QLabel("Sin ventas registradas aún.", styleSheet="color: #64748B; font-size: 12px; margin-top: 10px;"))
        top_vbox.addStretch()
        mid_layout.addWidget(top_card, stretch=1)
        left_layout.addLayout(mid_layout)

        # Inventario y Producción (AHORA CONECTADO A LA BD)
        bot_layout = QHBoxLayout()
        bot_layout.setSpacing(12)

        inv_card = ModernCard(border_color=COLOR_NAVY)
        inv_vbox = QVBoxLayout(inv_card)
        inv_vbox.setContentsMargins(14, 14, 14, 14)
        
        inv_header = QHBoxLayout()
        inv_header.addWidget(QLabel("📦 Inventario Actual", styleSheet=f"font-size: 14px; font-weight: bold; color: {COLOR_NAVY};"))
        inv_header.addStretch()
        
        btn_ver_inv = QPushButton("Ver completo ➔")
        btn_ver_inv.setFixedHeight(24)
        btn_ver_inv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ver_inv.setStyleSheet(f"background-color: {COLOR_NAVY}; color: white; padding: 0 8px; border-radius: 5px; font-size: 10px; font-weight: bold;")
        btn_ver_inv.clicked.connect(lambda: self.switch_view_callback("inv_granel"))
        inv_header.addWidget(btn_ver_inv)
        inv_vbox.addLayout(inv_header)

        # Contenedor dinámico para la lista de productos de la BD
        self.grid_inv = QGridLayout()
        self.cargar_stock_inicio()
        inv_vbox.addLayout(self.grid_inv)
        
        bot_layout.addWidget(inv_card, stretch=1)

        prod_card = ModernCard(border_color=COLOR_NAVY)
        prod_vbox = QVBoxLayout(prod_card)
        prod_vbox.setContentsMargins(14, 14, 14, 14)
        prod_vbox.addWidget(QLabel("⚙️ Producción", styleSheet=f"font-size: 14px; font-weight: bold; color: {COLOR_NAVY};"))
        prod_vbox.addWidget(QLabel("0 L Producidos / Meta: 0 L", styleSheet="color: #4B5563; font-size: 12px;"))
        prod_vbox.addStretch()
        bot_layout.addWidget(prod_card, stretch=1)

        left_layout.addLayout(bot_layout)
        master_layout.addWidget(left_container, stretch=3)

        # Panel Alertas y Trazabilidad
        right_panel = QWidget()
        right_panel.setFixedWidth(300)
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(16)

        alert_card = ModernCard(border_color=COLOR_NAVY)
        alert_vbox = QVBoxLayout(alert_card)
        alert_vbox.setContentsMargins(12, 12, 12, 12)
        alert_vbox.addWidget(QLabel("🔔 Alertas y vencimientos", styleSheet=f"font-size: 12px; font-weight: bold; color: {COLOR_NAVY};"))
        alert_vbox.addWidget(QLabel("No hay alertas pendientes.", styleSheet="color: #64748B; font-size: 11px; margin-top: 5px;"))
        right_panel_layout.addWidget(alert_card)

        traz_card = ModernCard(border_color=COLOR_NAVY)
        traz_vbox = QVBoxLayout(traz_card)
        traz_vbox.setContentsMargins(12, 12, 12, 12)
        traz_vbox.addWidget(QLabel("🔍 Trazabilidad", styleSheet=f"font-size: 12px; font-weight: bold; color: {COLOR_NAVY};"))
        traz_vbox.addWidget(QLabel("Desde la materia prima hasta el cliente", styleSheet="color: #64748B; font-size: 10px;"))
        btn_t = QPushButton("Ver trazabilidad >")
        btn_t.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_t.setStyleSheet(f"background-color: {COLOR_NAVY}; color: white; font-weight: bold; border-radius: 6px; padding: 6px;")
        btn_t.clicked.connect(lambda: self.switch_view_callback("trazabilidad"))
        traz_vbox.addWidget(btn_t)
        right_panel_layout.addWidget(traz_card)
        right_panel_layout.addStretch()

        master_layout.addWidget(right_panel)

    def cargar_stock_inicio(self):
        """ Consulta los datos reales de la BD para mostrarlos en el Dashboard """
        self.grid_inv.addWidget(QLabel("<b>Producto / Material</b>"), 0, 0)
        self.grid_inv.addWidget(QLabel("<b>Lote</b>"), 0, 1)
        self.grid_inv.addWidget(QLabel("<b>Cantidad</b>"), 0, 2)
        self.grid_inv.addWidget(QLabel("<b>Estado</b>"), 0, 3)

        # Traemos los datos reales usando la vista PEPS de la base de datos
        try:
            productos = self.db.obtener_inventario_resumen("GRANEL")
            if not productos:
                # Si no hay granel, probamos con unidades
                productos = self.db.obtener_inventario_resumen("UNIDADES")
            
            if productos:
                for i, prod in enumerate(productos[:5], start=1):  # Muestra hasta 5 productos
                    self.grid_inv.addWidget(QLabel(str(prod.get("material", "N/A")), styleSheet="font-size: 11px;"), i, 0)
                    self.grid_inv.addWidget(QLabel(str(prod.get("numero_lote", "N/A")), styleSheet="font-size: 11px;"), i, 1)
                    cant = f"{prod.get('cantidad_actual', 0):.1f} {prod.get('unidad_medida', '')}"
                    self.grid_inv.addWidget(QLabel(cant, styleSheet="font-size: 11px;"), i, 2)
                    
                    lbl_st = QLabel(" Normal ")
                    lbl_st.setStyleSheet("background-color: #D1FAE5; color: #065F46; border-radius: 4px; font-size: 10px;")
                    self.grid_inv.addWidget(lbl_st, i, 3)
            else:
                self.grid_inv.addWidget(QLabel("No hay productos registrados en la BD.", styleSheet="color: #64748B; font-size: 11px;"), 1, 0, 1, 4)
        except Exception as e:
            self.grid_inv.addWidget(QLabel(f"Error al cargar stock: {str(e)}", styleSheet="color: red; font-size: 10px;"), 1, 0, 1, 4)
# VENTAS 
class SalesView(QWidget):
    def __init__(self, mode="Diario"):
        super().__init__()
        self.mode = mode
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl = QLabel(f"🛒  Ventas - {self.mode}")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(lbl)

        kpi_row = QHBoxLayout()
        kpi_row.addWidget(StatCard("🛒", f"Total ventas ({self.mode.lower()})", "Bs. 0,00", "0% vs. periodo anterior"))
        kpi_row.addWidget(StatCard("📄", "Transacciones", "0", "0% vs. periodo anterior"))
        layout.addLayout(kpi_row)

        table_card = ModernCard(border_color=COLOR_NAVY)
        tvbox = QVBoxLayout(table_card)
        tvbox.setContentsMargins(16, 16, 16, 16)
        tvbox.addWidget(QLabel(f"Registro de Transacciones - {self.mode}", styleSheet=f"font-size: 14px; font-weight: bold; color: {COLOR_NAVY};"))
        
        grid = QGridLayout()
        for idx, h in enumerate(["N°", "Producto", "Cantidad", "Precio unit.", "Total", "Fecha/Hora"]):
            grid.addWidget(QLabel(f"<b>{h}</b>", styleSheet="color: #475569;"), 0, idx)
        
        for r in range(1, 6):
            grid.addWidget(QLabel(f"00{r}"), r, 0)
            grid.addWidget(QLabel("Detergente / Limpiador"), r, 1)
            grid.addWidget(QLabel("0"), r, 2)
            grid.addWidget(QLabel("0,00"), r, 3)
            grid.addWidget(QLabel("0,00", styleSheet="font-weight: bold;"), r, 4)
            grid.addWidget(QLabel("05/06/2026"), r, 5)
        tvbox.addLayout(grid)
        layout.addWidget(table_card)
        layout.addStretch()

# INVENTARIO (GRANEL, UNIDAD)
class InventoryView(QWidget):
    def __init__(self, mode="GRANEL"):
        super().__init__()
        self.mode = mode.upper()
        self.db = DatabaseManager()
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Encabezado
        h_layout = QHBoxLayout()
        lbl = QLabel(f"📦 Inventario - Sector {self.mode}")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLOR_NAVY};")
        
        btn_refresh = QPushButton("🔄 Actualizar Tabla")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"background-color: {COLOR_NAVY}; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        btn_refresh.clicked.connect(self.cargar_datos)
        
        h_layout.addWidget(lbl)
        h_layout.addStretch()
        h_layout.addWidget(btn_refresh)
        layout.addLayout(h_layout)

        # Tabla de datos
        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["Código", "Material", "N° Lote", "Cantidad Disponible", "Ubicación / Tanque"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setStyleSheet(f"""
            QTableWidget {{ background-color: #FFFFFF; border: 1px solid #CBD5E1; font-size: 13px; gridline-color: #F1F5F9; }}
            QHeaderView::section {{ background-color: {COLOR_NAVY}; color: #FFFFFF; font-weight: bold; padding: 8px; border: none; }}
        """)
        layout.addWidget(self.tabla)
        
        self.cargar_datos()

    def cargar_datos(self):
        """ Consulta a la vista v_inventario_peps de la BD """
        datos = self.db.obtener_inventario_resumen(self.mode)
        self.tabla.setRowCount(len(datos))
        for fila, reg in enumerate(datos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(reg.get("codigo", "N/A"))))
            self.tabla.setItem(fila, 1, QTableWidgetItem(str(reg["material"])))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(reg["numero_lote"])))
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"{reg['cantidad_actual']:.2f} {reg['unidad_medida']}"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(str(reg["tanque_almacenamiento"] or "Almacén Central")))

# VISTA DE TRAZABILIDAD SENASAG
class VistaTrazabilidadSENASAG(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        
        lbl_titulo = QLabel("🔍 Trazabilidad de Producción (SENASAG)")
        lbl_titulo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COLOR_NAVY}; margin-bottom: 10px;")
        layout.addWidget(lbl_titulo)

        self.tabla = QTableWidget(0, 7)
        self.tabla.setHorizontalHeaderLabels([
            "Lote Prod. Final", "Producto", "Fecha Prod.", 
            "Insumo Utilizado", "Sector", "Lote Insumo", "Cant. Descontada"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setStyleSheet(f"""
            QTableWidget {{ background-color: #FFFFFF; border: 1px solid #CBD5E1; font-size: 12px; gridline-color: #F1F5F9; }}
            QHeaderView::section {{ background-color: {COLOR_NAVY}; color: #FFFFFF; font-weight: bold; padding: 8px; border: none; }}
        """)
        
        layout.addWidget(self.tabla)
        self.cargar_trazabilidad()

    def cargar_trazabilidad(self):
        datos = self.db.obtener_trazabilidad_senasag()
        self.tabla.setRowCount(len(datos))
        for fila, reg in enumerate(datos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(reg["lote_producto_final"])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(str(reg["producto"])))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(reg["fecha_produccion"])))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(reg["insumo_utilizado"])))
            self.tabla.setItem(fila, 4, QTableWidgetItem(str(reg["tipo_insumo"])))
            self.tabla.setItem(fila, 5, QTableWidgetItem(str(reg["lote_origen_insumo"])))
            self.tabla.setItem(fila, 6, QTableWidgetItem(f"{reg['cantidad_descontada']:.2f}"))

# VISTAS GENÉRICAS
class GenericModuleView(QWidget):
    def __init__(self, title, description):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLOR_BG};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLOR_NAVY};")
        layout.addWidget(lbl)

        card = ModernCard(border_color=COLOR_NAVY)
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(24, 24, 24, 24)
        vbox.addWidget(QLabel(description, styleSheet=f"color: {COLOR_TEXT_MUTED}; font-size: 14px;"))
        vbox.addSpacing(10)
        
        vbox.addWidget(QLabel("Estado actual: Sin registros cargados o en espera de base de datos.", styleSheet=f"color: {COLOR_NAVY}; font-weight: bold;"))
        layout.addWidget(card)
        layout.addStretch()

# VENTANA PRINCIPAL 
class MainSystemWindow(QMainWindow):
    def __init__(self, username="Administrador", on_logout=None):
        super().__init__()
        self.username = username
        self.on_logout_callback = on_logout
        self.setWindowTitle("KING CLEANER - Sistema de Control e Inventario")
        self.resize(1366, 768)
        self.nav_buttons = {}
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra Lateral
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background-color: {COLOR_NAVY}; color: #FFFFFF;")

        self.sidebar_layout = QVBoxLayout(sidebar)
        self.sidebar_layout.setContentsMargins(14, 16, 14, 16)
        self.sidebar_layout.setSpacing(6)

        brand_layout = QHBoxLayout()
        brand_layout.addWidget(KingCleanerLogoWidget(size=46))
        text_brand = QVBoxLayout()
        lbl_b = QLabel("KING CLEANER")
        lbl_b.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_b.setStyleSheet(f"color: {COLOR_GOLD}; border: none;")
        lbl_s = QLabel("Control e Inventario")
        lbl_s.setStyleSheet("color: #94A3B8; font-size: 9px; border: none;")
        text_brand.addWidget(lbl_b)
        text_brand.addWidget(lbl_s)
        brand_layout.addLayout(text_brand)
        self.sidebar_layout.addLayout(brand_layout)
        self.sidebar_layout.addSpacing(12)

        # Botón Inicio
        self.btn_inicio = self.create_nav_btn("inicio", "🏠  Inicio", lambda: self.switch_to("inicio"))

        # Menú Ventas 
        self.btn_ventas = self.create_nav_btn("ventas", "🛒  Ventas ▾", self.toggle_sales_menu)
        self.sales_sub_widget = QWidget()
        s_vbox = QVBoxLayout(self.sales_sub_widget)
        s_vbox.setContentsMargins(18, 0, 0, 4)
        s_vbox.setSpacing(2)
        self.btn_v_diario = self.create_sub_btn("• Diario", lambda: self.switch_to("ventas_diario"))
        self.btn_v_mensual = self.create_sub_btn("• Mensual", lambda: self.switch_to("ventas_mensual"))
        self.btn_v_anual = self.create_sub_btn("• Anual", lambda: self.switch_to("ventas_anual"))
        s_vbox.addWidget(self.btn_v_diario)
        s_vbox.addWidget(self.btn_v_mensual)
        s_vbox.addWidget(self.btn_v_anual)
        self.sales_sub_widget.hide()

        # Menú Inventario
        self.btn_inventario = self.create_nav_btn("inventario", "📦  Inventario ▾", self.toggle_inv_menu)
        self.inv_sub_widget = QWidget()
        i_vbox = QVBoxLayout(self.inv_sub_widget)
        i_vbox.setContentsMargins(18, 0, 0, 4)
        i_vbox.setSpacing(2)
        self.btn_i_granel = self.create_sub_btn("• A granel", lambda: self.switch_to("inv_granel"))
        self.btn_i_unidad = self.create_sub_btn("• Por unidad", lambda: self.switch_to("inv_unidad"))
        i_vbox.addWidget(self.btn_i_granel)
        i_vbox.addWidget(self.btn_i_unidad)
        self.inv_sub_widget.hide()

        # Botones del Menú Principal
        self.btn_produccion = self.create_nav_btn("produccion", "⚙️  Producción", lambda: self.switch_to("produccion"))
        self.btn_trazabilidad = self.create_nav_btn("trazabilidad", "🔍  Trazabilidad", lambda: self.switch_to("trazabilidad"))
        self.btn_alertas = self.create_nav_btn("alertas", "🔔  Alertas (0)", lambda: self.switch_to("alertas"))
        self.btn_reportes = self.create_nav_btn("reportes", "📄  Reportes", lambda: self.switch_to("reportes"))
        self.btn_config = self.create_nav_btn("config", "⚙️  Configuración", lambda: self.switch_to("config"))

        # Añadir al Sidebar
        for w in [self.btn_inicio, self.btn_ventas, self.sales_sub_widget, 
                  self.btn_inventario, self.inv_sub_widget, self.btn_produccion, 
                  self.btn_trazabilidad, self.btn_alertas, self.btn_reportes, self.btn_config]:
            self.sidebar_layout.addWidget(w)

        self.sidebar_layout.addStretch()
        
        lbl_phrase = QLabel("¡Juntos hacemos\nla diferencia!")
        lbl_phrase.setStyleSheet(f"color: {COLOR_GOLD}; font-style: italic; font-size: 11px;")
        self.sidebar_layout.addWidget(lbl_phrase)
        self.sidebar_layout.addSpacing(6)

        btn_out = QPushButton("🚪  Cerrar Sesión")
        btn_out.setStyleSheet("background-color: transparent; color: #94A3B8; text-align: left; padding-left: 12px; font-size: 12px; border: none;")
        btn_out.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_out.clicked.connect(self.on_logout_callback)
        self.sidebar_layout.addWidget(btn_out)

        layout.addWidget(sidebar)

        # Contenedor Derecho 
        right_container = QWidget()
        right_container.setStyleSheet(f"background-color: {COLOR_BG};")
        r_layout = QVBoxLayout(right_container)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(0)

        # Header Superior
        header = QFrame()
        header.setFixedHeight(54)
        header.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)
        h_layout.addWidget(QLabel("Control total, mejores decisiones", styleSheet=f"color: {COLOR_TEXT_MUTED}; font-size: 12px;"))
        h_layout.addStretch()
        h_layout.addWidget(QLabel(f"👤 Usuario: {self.username}", styleSheet=f"color: {COLOR_NAVY}; font-size: 12px; font-weight: bold;"))
        h_layout.addWidget(QLabel("📅 05 de Junio de 2026\n     10:24 a.m.", styleSheet="color: #64748B; font-size: 11px;"))
        r_layout.addWidget(header)

        # Stack de Páginas
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COLOR_BG};")

        # Instanciar Vistas
        self.p_inicio = HomeDashboardView(self.switch_to)
        self.p_v_diario = SalesView("Diario")
        self.p_v_mensual = SalesView("Mensual")
        self.p_v_anual = SalesView("Anual")
        
        self.p_i_granel = InventoryView("GRANEL")
        self.p_i_unidad = InventoryView("UNIDADES")
        
        self.p_produccion = GenericModuleView("⚙️ Producción", "Módulo de producción.")
        self.p_trazabilidad = VistaTrazabilidadSENASAG()
        
        self.p_alertas = GenericModuleView("🔔 Alertas", "Módulo de alertas.")
        self.p_reportes = GenericModuleView("📄 Reportes", "Módulo de reportes.")
        self.p_config = GenericModuleView("⚙️ Configuración", "Módulo de configuración.")

        # Agregar al QStackedWidget
        for widget in [self.p_inicio, self.p_v_diario, self.p_v_mensual, self.p_v_anual, 
                      self.p_i_granel, self.p_i_unidad, self.p_produccion, self.p_trazabilidad, 
                      self.p_alertas, self.p_reportes, self.p_config]:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet(f"QScrollArea {{ border: none; background-color: {COLOR_BG}; }}")
            scroll.setWidget(widget)
            self.stack.addWidget(scroll)

        r_layout.addWidget(self.stack)
        layout.addWidget(right_container)

        self.switch_to("inicio")

    def create_nav_btn(self, key, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        self.nav_buttons[key] = btn
        return btn

    def create_sub_btn(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("QPushButton { background-color: transparent; color: #94A3B8; text-align: left; padding-left: 10px; font-size: 11px; border: none; } QPushButton:hover { color: #FFFFFF; }")
        btn.clicked.connect(callback)
        return btn

    def toggle_sales_menu(self):
        self.sales_sub_widget.setVisible(not self.sales_sub_widget.isVisible())

    def toggle_inv_menu(self):
        self.inv_sub_widget.setVisible(not self.inv_sub_widget.isVisible())

    def switch_to(self, view_key):
        mapping = {
            "inicio": 0,
            "ventas_diario": 1,
            "ventas_mensual": 2,
            "ventas_anual": 3,
            "inv_granel": 4,
            "inv_unidad": 5,
            "produccion": 6,
            "trazabilidad": 7,
            "alertas": 8,
            "reportes": 9,
            "config": 10
        }
        
        if view_key in mapping:
            self.stack.setCurrentIndex(mapping[view_key])

        for k, btn in self.nav_buttons.items():
            active = False
            if view_key == "inicio" and k == "inicio":
                active = True
            elif view_key.startswith("ventas") and k == "ventas":
                active = True
            elif view_key.startswith("inv") and k == "inventario":
                active = True
            elif view_key == k:
                active = True

            if active:
                btn.setStyleSheet(f"QPushButton {{ background-color: {COLOR_ORANGE}; color: #FFFFFF; text-align: left; padding-left: 14px; border-radius: 8px; font-weight: bold; font-size: 12px; border: none; }}")
            else:
                btn.setStyleSheet("QPushButton { background-color: transparent; color: #94A3B8; text-align: left; padding-left: 14px; border-radius: 8px; font-size: 12px; border: none; } QPushButton:hover { background-color: #1E1B4B; color: #FFFFFF; }")

# CONTROLADOR GLOBAL (LOGIN -> REGISTRO -> SISTEMA)
class AppController(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.login_win = LoginWindow(self.show_main, self.show_register)
        self.register_win = RegisterWindow(self.show_login)
        
        self.addWidget(self.login_win)    # Índice 0
        self.addWidget(self.register_win) # Índice 1
        self.setCurrentIndex(0)

    def show_login(self):
        self.setCurrentIndex(0)

    def show_register(self):
        self.setCurrentIndex(1)

    def show_main(self, username):
        self.main_sys = MainSystemWindow(username=username, on_logout=self.show_login)
        self.addWidget(self.main_sys)
        self.setCurrentWidget(self.main_sys)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    controller.resize(1280, 720)
    controller.show()
    sys.exit(app.exec())