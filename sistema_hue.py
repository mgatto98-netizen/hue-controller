#!/usr/bin/env python3
# app_hue_mejorada.py
# Aplicación para controlar luces Philips Hue en Linux

import sys, os as _os
_venv_sp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'venv', 'lib', 'python3.10', 'site-packages')
if _os.path.exists(_venv_sp) and _venv_sp not in sys.path:
    sys.path.insert(0, _venv_sp)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import requests
import threading
import sys
import os
import json
import datetime
import time
import struct
import queue

# Ícono de la aplicación embebido en base64
APP_ICON_B64 = """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"""


class AppHueMejorada(Gtk.Window):
    def __init__(self):
        super().__init__(title="")  # se setea después de cargar config
        
        # Configuración de la ventana
        self.set_default_size(1200, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(900, 500)

        # Aplicar ícono del gatito
        try:
            import base64, io
            from gi.repository import GdkPixbuf
            icon_data = base64.b64decode(APP_ICON_B64)
            loader = GdkPixbuf.PixbufLoader.new_with_type("png")
            loader.write(icon_data)
            loader.close()
            self.set_icon(loader.get_pixbuf())
        except Exception as e:
            print(f"No se pudo cargar el ícono: {e}") 
        self.set_resizable(True)  
        # Variables
        self.bridge_ip = None
        self.api_key = None
        self.headers = None
        self._actualizando_switch_habitacion = False
        
        # Datos de la API
        self.rooms = {}
        self.devices = {}
        self.sensors = {}
        self.scenes = {}
        self.scenes_by_room = {}
        
        # Configuración de actualización
        self.update_interval = 300
        self.update_timer = None
        
        # Archivo de configuración
        self.config_file = os.path.expanduser("~/.hue_controller_config.json")
        self.config = self.cargar_configuracion()
        
        if "update_interval" in self.config:
            self.update_interval = self.config["update_interval"]

        titulo_app = self.config.get("titulo_app", "Sistema Hue")
        self.set_title(titulo_app)

        # Estilo CSS
        self.aplicar_estilos()
        
        # Crear la interfaz
        self.crear_interfaz()
        
        # Si hay IP y API Key guardadas, intentar conectar automáticamente
        if self.config.get("bridge_ip") and self.config.get("api_key"):
            GLib.idle_add(lambda: self.on_conectar_clicked(None))
        elif not self.config.get("bridge_ip"):
            GLib.idle_add(self.on_buscar_bridge_clicked, None)
        
        self.show_all()
    
    def cargar_configuracion(self):
        """Carga la configuración guardada"""
        config_default = {
            "bridge_ip": "",
            "api_key": "",
            "update_interval": 300,
            "app_name": "hue_controller_linux",
            "ent_username": "",
            "ent_clientkey": "",
            "titulo_app": "Sistema Hue"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    for key in config_default:
                        if key not in config:
                            config[key] = config_default[key]
                    return config
        except Exception as e:
            print(f"Error cargando configuración: {e}")
        
        return config_default
    
    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def aplicar_estilos(self):
        """Aplica estilos CSS personalizados"""
        css = """
        * {
            font-family: 'Segoe UI', 'Ubuntu', 'Cantarell', sans-serif;
        }
        
        .sidebar {
            background-color: #2c3e50;
            padding: 10px;
        }
        
        .sidebar button {
            background-color: #34495e;
            background-image: none;
            color: white;
            border: none;
            padding: 12px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 14px;
        }

        .sidebar button label {
            color: white;
        }

        .sidebar button:hover {
            background-color: #3498db;
            background-image: none;
        }

        .sidebar button:hover label {
            color: white;
        }

        .sidebar button:active {
            background-color: #2980b9;
            background-image: none;
        }
        
        .card-luz {
            background-color: #ecf0f1;
            border-radius: 8px;
            padding: 8px 12px;
            margin: 5px 0;
            border: 1px solid #bdc3c7;
        }
        
        .card-luz:hover {
            background-color: #e0e4e5;
            border-color: #3498db;
        }
        
        .nombre-luz {
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .info-panel {
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        .slider {

            margin: 0 10px;
        }

        .compact-slider trough {
            min-height: 4px;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        .compact-slider slider {
            min-width: 14px;
            min-height: 14px;
        }
        
        .brillo-icono {
            font-size: 16px;
            margin-right: 5px;
        }
        
        .habitacion-item {
            background-color: #34495e;
            color: white;
            border-radius: 5px;
            padding: 5px;
            margin: 2px 0;
        }
        
        .habitacion-item:hover {
            background-color: #3b5a7a;
        }
        
        .sensor-card {
            background: linear-gradient(135deg, #2c3e6b 0%, #4a2c6b 100%);
            border-radius: 10px;
            padding: 8px 10px;
            margin: 3px 4px;
            color: white;
            min-width: 180px;
            border: 1px solid rgba(255,255,255,0.15);
        }

        .sensor-temperatura {
            color: #a0d8ff;
        }

        .sensor-ubicacion {
            font-size: 13px;
            font-weight: bold;
        }

        .sensor-updated {
            font-size: 13px;
        }

        .sensores-bar {
            border-radius: 8px;
        }

        .btn-baterias {
            border-radius: 8px;
            padding: 6px;
        }

        .bateria-card {
            border-radius: 10px;
            padding: 12px;
            margin: 4px;
            border: 1px solid alpha(currentColor, 0.15);
        }

        .bateria-card-ok {
            background: linear-gradient(135deg, #1a3a2a 0%, #1a3a1a 100%);
            color: white;
        }

        .bateria-card-media {
            background: linear-gradient(135deg, #3a3010 0%, #3a2a00 100%);
            color: white;
        }

        .bateria-card-baja {
            background: linear-gradient(135deg, #3a1010 0%, #2a0a0a 100%);
            color: white;
        }

        .bateria-nivel {
            font-size: 22px;
            font-weight: bold;
        }

        .bateria-nombre {
            font-size: 12px;
        }

        .bateria-tipo {
            font-size: 10px;
            color: #aaaaaa;
        }
        
        .config-box {
            background-color: #ecf0f1;
            border-radius: 5px;
            padding: 5px;
            margin-top: 5px;
        }
        
        .escenas-container {
            background-color: transparent;
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        }
        
        .escena-boton {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 8px;
            margin: 5px;
        }
        
        .escena-boton:hover {
            background-color: #e9ecef;
            border-color: #9b59b6;
        }
        
        .escena-icono {
            font-size: 32px;
            margin-bottom: 5px;
        }
        
        .escena-nombre {
            font-size: 11px;
            color: #495057;
        }
        
        .btn-color {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #bdc3c7;
            border-radius: 50%;
            padding: 1px 12px;
            font-size: 18px;
            min-width: 45px;
            min-height: 35px;
        }
        
        .btn-color:hover {
            background-color: #f0f0f0;
            border-color: #9b59b6;
        }
        
        .btn-color:active {
            background-color: #e0e0e0;
        }
        """
        
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css.encode('utf-8'))

        def _apply_on_realize(widget):
            screen = widget.get_screen()
            if screen:
                Gtk.StyleContext.add_provider_for_screen(
                    screen,
                    style_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_USER
                )

        self.connect("realize", _apply_on_realize)


    def _actualizar_titulo_label(self):
        titulo = self.config.get("titulo_app", "Sistema Hue")
        self.titulo_label.set_markup(f"<span size='x-large' weight='bold'>🏠 {titulo}</span>")

    def on_cambiar_titulo_clicked(self, widget):
        dialogo = Gtk.Dialog(title="Cambiar nombre de la app", transient_for=self, modal=True)
        dialogo.set_default_size(360, 120)
        content = dialogo.get_content_area()
        content.set_spacing(10)
        content.set_margin_top(16)
        content.set_margin_bottom(10)
        content.set_margin_start(16)
        content.set_margin_end(16)

        lbl = Gtk.Label(label="Nombre de la aplicación:")
        lbl.set_halign(Gtk.Align.START)
        content.add(lbl)

        entry = Gtk.Entry()
        entry.set_text(self.config.get("titulo_app", "Sistema Hue"))
        entry.set_activates_default(True)
        content.add(entry)

        dialogo.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        btn_ok = dialogo.add_button("Guardar", Gtk.ResponseType.OK)
        btn_ok.set_can_default(True)
        btn_ok.grab_default()

        dialogo.show_all()
        resp = dialogo.run()
        nuevo = entry.get_text().strip()
        dialogo.destroy()

        if resp == Gtk.ResponseType.OK and nuevo:
            self.config["titulo_app"] = nuevo
            self.guardar_configuracion()
            self.set_title(nuevo)
            self._actualizar_titulo_label()

    def crear_interfaz(self):
        """Crea la interfaz principal de la aplicación"""
        # Panel principal horizontal
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.paned)
        
        # --- Sidebar izquierdo ---
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.sidebar.set_size_request(380, -1)
        self.sidebar.get_style_context().add_class("sidebar")
        
        # Título (click para editar)
        self.titulo_label = Gtk.Label()
        self._actualizar_titulo_label()
        self.titulo_label.set_margin_top(20)
        self.titulo_label.set_margin_bottom(5)

        btn_titulo = Gtk.Button()
        btn_titulo.set_relief(Gtk.ReliefStyle.NONE)
        btn_titulo.add(self.titulo_label)
        btn_titulo.set_tooltip_text("Click para cambiar el nombre de la app")
        btn_titulo.connect("clicked", self.on_cambiar_titulo_clicked)
        self.sidebar.pack_start(btn_titulo, False, False, 0)
        
        # Frame de conexión
        frame_conexion = Gtk.Frame(label="🔌 Conexión")
        frame_conexion.set_margin_top(10)
        frame_conexion.set_margin_bottom(10)
        box_conexion = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box_conexion.set_margin_top(10)
        box_conexion.set_margin_bottom(10)
        box_conexion.set_margin_start(10)
        box_conexion.set_margin_end(10)
        
        # IP Entry
        ip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ip_box.pack_start(Gtk.Label(label="IP del puente:"), False, False, 0)
        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_placeholder_text("192.168.1.x")
        self.ip_entry.set_text(self.config.get("bridge_ip", ""))
        ip_box.pack_start(self.ip_entry, True, True, 0)
        box_conexion.pack_start(ip_box, False, False, 0)
        
        # Botones buscar + conectar
        btn_acciones = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.btn_buscar_bridge = Gtk.Button(label="🔍 Buscar")
        self.btn_buscar_bridge.set_tooltip_text("Buscar bridge Hue en la red WiFi automáticamente")
        self.btn_buscar_bridge.connect("clicked", self.on_buscar_bridge_clicked)
        btn_acciones.pack_start(self.btn_buscar_bridge, True, True, 0)
        self.btn_conectar = Gtk.Button(label="🔌 Conectar")
        self.btn_conectar.connect("clicked", self.on_conectar_clicked)
        btn_acciones.pack_start(self.btn_conectar, True, True, 0)
        btn_acciones.set_margin_bottom(5)
        box_conexion.pack_start(btn_acciones, False, False, 0)
        
        # Estado de conexión
        self.label_estado = Gtk.Label()
        self.label_estado.set_markup("<span foreground='orange'>⚪ Estado: No conectado</span>")
        box_conexion.pack_start(self.label_estado, False, False, 0)
        
        frame_conexion.add(box_conexion)
        self.sidebar.pack_start(frame_conexion, False, False, 0)
        
        # Lista de habitaciones
        self.scroll_habitaciones = Gtk.ScrolledWindow()
        self.scroll_habitaciones.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_habitaciones.set_min_content_height(80)
        
        self.lista_habitaciones = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.lista_habitaciones.set_margin_top(10)
        self.lista_habitaciones.set_margin_bottom(10)
        self.lista_habitaciones.set_margin_start(10)
        self.lista_habitaciones.set_margin_end(10)
        
        self.scroll_habitaciones.add(self.lista_habitaciones)
        
        # Paned vertical: reparte el espacio disponible entre habitaciones y sensores
        # Habitaciones con label
        label_habitaciones = Gtk.Label()
        label_habitaciones.set_markup("<span weight='bold'>🏠 Habitaciones</span>")
        label_habitaciones.set_margin_top(5)
        label_habitaciones.set_margin_bottom(5)
        self.sidebar.pack_start(label_habitaciones, False, False, 0)
        self.sidebar.pack_start(self.scroll_habitaciones, True, True, 0)
        
        # Fila con botones de baterías y dimmers
        sep_baterias = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.sidebar.pack_start(sep_baterias, False, False, 5)

        fila_botones = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        fila_botones.set_margin_start(10)
        fila_botones.set_margin_end(10)
        fila_botones.set_margin_bottom(5)

        btn_baterias = Gtk.Button()
        btn_baterias.set_tooltip_text("Ver estado de baterías")
        btn_baterias.get_style_context().add_class("btn-baterias")
        hbox_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        hbox_btn.set_halign(Gtk.Align.CENTER)

        self._bat_color = (0.2, 0.8, 0.2)
        self._bat_nivel = 100
        self._bat_image = Gtk.Image()
        self._bat_image.set_size_request(28, 16)
        self._actualizar_imagen_bateria()

        hbox_btn.pack_start(self._bat_image, False, False, 0)
        hbox_btn.pack_start(Gtk.Label(label="Baterías"), False, False, 0)
        btn_baterias.add(hbox_btn)
        btn_baterias.connect("clicked", self.on_baterias_clicked)

        btn_dimmers = Gtk.Button(label="🔘 Dimmers")
        btn_dimmers.set_tooltip_text("Ver escenas configuradas en cada dimmer")
        btn_dimmers.get_style_context().add_class("btn-baterias")
        btn_dimmers.connect("clicked", self.on_dimmers_clicked)

        fila_botones.pack_start(btn_baterias, True, True, 0)
        fila_botones.pack_start(btn_dimmers, True, True, 0)
        self.sidebar.pack_start(fila_botones, False, False, 0)

        btn_musica = Gtk.Button(label="🎵 Música")
        btn_musica.set_tooltip_text("Sincronizar luces con la música")
        btn_musica.get_style_context().add_class("btn-baterias")
        btn_musica.set_margin_start(10)
        btn_musica.set_margin_end(10)
        btn_musica.set_margin_bottom(2)
        btn_musica.connect("clicked", self.on_musica_clicked)
        self.sidebar.pack_start(btn_musica, False, False, 0)

        # Configuración de intervalo de actualización (compacta, al fondo)
        config_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        config_row.set_margin_start(12)
        config_row.set_margin_end(12)
        config_row.set_margin_bottom(6)
        config_row.pack_start(Gtk.Label(label="⚙️ Sensores cada:"), False, False, 0)
        self.update_spin = Gtk.SpinButton()
        self.update_spin.set_range(1, 60)
        self.update_spin.set_value(self.update_interval / 60)
        self.update_spin.set_digits(0)
        self.update_spin.set_increments(1, 5)
        self.update_spin.set_size_request(55, -1)
        self.update_spin.connect("value-changed", self.on_update_interval_changed)
        config_row.pack_start(self.update_spin, False, False, 0)
        config_row.pack_start(Gtk.Label(label="min"), False, False, 0)
        self.sidebar.pack_start(config_row, False, False, 0)

        # Spinner de carga
        self.spinner = Gtk.Spinner()
        self.sidebar.pack_start(self.spinner, False, False, 10)
        
        self.paned.pack1(self.sidebar, False, False)
        
        # --- Panel derecho ---
        self.panel_derecho = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.panel_derecho.set_margin_top(20)
        self.panel_derecho.set_margin_bottom(20)
        self.panel_derecho.set_margin_start(20)
        self.panel_derecho.set_margin_end(20)
        
        # Panel de información
        self.info_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.info_panel.get_style_context().add_class("info-panel")
        self.panel_derecho.pack_start(self.info_panel, False, False, 0)
        
        self.nombre_habitacion_label = Gtk.Label()
        self.nombre_habitacion_label.set_markup("<span size='x-large' weight='bold'>Selecciona una habitación</span>")
        self.info_panel.pack_start(self.nombre_habitacion_label, False, False, 5)
        
        # Separador
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.panel_derecho.pack_start(separator2, False, False, 10)
        
        # Barra de sensores de temperatura
        self.sensores_frame = Gtk.Frame()
        self.sensores_frame.get_style_context().add_class("sensores-bar")
        self.sensores_frame.set_label(" 🌡️ TEMPERATURAS ")
        self.sensores_frame.set_label_align(0.0, 0.5)

        self.sensores_scroll = Gtk.ScrolledWindow()
        self.sensores_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.sensores_scroll.set_min_content_height(90)

        self.sensores_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.sensores_container.set_margin_top(8)
        self.sensores_container.set_margin_bottom(8)
        self.sensores_container.set_margin_start(10)
        self.sensores_container.set_margin_end(10)

        self.sensores_scroll.add(self.sensores_container)
        self.sensores_frame.add(self.sensores_scroll)
        self.panel_derecho.pack_start(self.sensores_frame, False, False, 0)

        separator_sensores = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.panel_derecho.pack_start(separator_sensores, False, False, 5)

        # Contenedor para escenas
        self.escenas_frame = Gtk.Frame()
        self.escenas_frame.get_style_context().add_class("escenas-container")
        self.escenas_frame.set_label(" ESCENAS ")
        self.escenas_frame.set_label_align(0.5, 0.5)
        
        self.escenas_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.escenas_box.set_margin_top(15)
        self.escenas_box.set_margin_bottom(10)
        self.escenas_box.set_margin_start(10)
        self.escenas_box.set_margin_end(10)
        
        self.escenas_scroll = Gtk.ScrolledWindow()
        self.escenas_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.escenas_scroll.set_min_content_height(80)
        
        self.escenas_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.escenas_container.set_margin_top(5)
        self.escenas_container.set_margin_bottom(5)
        
        self.escenas_scroll.add(self.escenas_container)
        self.escenas_box.pack_start(self.escenas_scroll, True, True, 0)
        self.escenas_frame.add(self.escenas_box)
        
        self.panel_derecho.pack_start(self.escenas_frame, False, False, 0)
        
        # Separador para escenas
        separator3 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.panel_derecho.pack_start(separator3, False, False, 10)
        
        # Scroll para las luces
        self.scroll_luces = Gtk.ScrolledWindow()
        self.scroll_luces.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll_luces.set_min_content_height(100)
        
        self.contenedor_luces = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.contenedor_luces.set_margin_top(5)
        
        self.scroll_luces.add(self.contenedor_luces)
        self.panel_derecho.pack_start(self.scroll_luces, True, True, 0)
        
        self.paned.pack2(self.panel_derecho, True, False)
        
        # Variables
        self.habitacion_actual = None
        self.botones_habitacion = {}
        self.switches_habitacion = {}
        self.switches_luces = {}
        self.sliders_luces = {}
        self.botones_color = {}
    
    def _render_battery_pixbuf(self, w, h, color, nivel):
        """Genera un GdkPixbuf con el ícono de batería usando Cairo — funciona en binarios compilados"""
        import cairo
        from gi.repository import GdkPixbuf, GLib
        r, g, b = color

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        cr = cairo.Context(surface)

        pole_w = w * 0.10
        pole_h = h * 0.35
        body_w = w - pole_w - 1
        body_h = float(h)
        radius = 2.5
        PI = 3.14159265358979

        # Cuerpo redondeado
        cr.new_sub_path()
        cr.arc(radius,           radius,           radius, PI,       3*PI/2)
        cr.arc(body_w - radius,  radius,           radius, 3*PI/2,   0)
        cr.arc(body_w - radius,  body_h - radius,  radius, 0,        PI/2)
        cr.arc(radius,           body_h - radius,  radius, PI/2,     PI)
        cr.close_path()
        cr.set_source_rgb(r * 0.55, g * 0.55, b * 0.55)
        cr.set_line_width(1.5)
        cr.stroke_preserve()
        cr.set_source_rgba(r * 0.2, g * 0.2, b * 0.2, 1.0)
        cr.fill()

        # Barra de carga
        padding = 3
        fill_w = max(0.0, (body_w - padding * 2) * (nivel / 100.0))
        cr.set_source_rgb(r, g, b)
        cr.rectangle(padding, padding, fill_w, body_h - padding * 2)
        cr.fill()

        # Polo positivo
        pole_x = body_w + 1
        pole_y = (body_h - pole_h) / 2
        cr.set_source_rgb(r * 0.65, g * 0.65, b * 0.65)
        cr.rectangle(pole_x, pole_y, pole_w, pole_h)
        cr.fill()

        # Convertir surface Cairo → GdkPixbuf
        data = surface.get_data()
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            data,
            GdkPixbuf.Colorspace.RGB,
            True, 8, w, h,
            surface.get_stride(),
        )
        # Cairo usa BGRA, GdkPixbuf espera RGBA — intercambiar canales R y B
        pixbuf2 = pixbuf.copy()
        arr = pixbuf2.get_pixels_array() if hasattr(pixbuf2, 'get_pixels_array') else None
        if arr is not None:
            arr[:,:,[0,2]] = arr[:,:,[2,0]]
        return pixbuf2

    def _actualizar_imagen_bateria(self):
        """Actualiza el Gtk.Image del botón con el pixbuf del ícono de batería"""
        try:
            nivel = self._bat_nivel if hasattr(self, '_bat_nivel') else 100
            pixbuf = self._render_battery_pixbuf(32, 18, self._bat_color, nivel)
            self._bat_image.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"Error dibujando ícono batería: {e}")

    def on_baterias_clicked(self, widget):
        """Abre la ventana de estado de baterías"""
        if not self.bridge_ip or not self.headers:
            self.mostrar_error("Conectate al bridge primero")
            return

        # Ventana de baterías
        dialog = Gtk.Window(title="🔋 Estado de Baterías")
        dialog.set_transient_for(self)
        dialog.set_default_size(700, 480)
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        dialog.set_resizable(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)
        vbox.set_margin_start(16)
        vbox.set_margin_end(16)
        dialog.add(vbox)

        # Header con título y botón refrescar
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        titulo = Gtk.Label()
        titulo.set_markup("<span size='large' weight='bold'>🔋 Estado de Baterías</span>")
        titulo.set_halign(Gtk.Align.START)
        header.pack_start(titulo, True, True, 0)

        btn_refresh = Gtk.Button(label="🔄 Actualizar")
        btn_refresh.set_halign(Gtk.Align.END)
        header.pack_start(btn_refresh, False, False, 0)
        vbox.pack_start(header, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(sep, False, False, 4)

        # Spinner mientras carga
        spinner = Gtk.Spinner()
        spinner.set_margin_top(40)
        spinner.set_margin_bottom(40)
        spinner.start()

        # ScrolledWindow con grid de tarjetas
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._bat_flowbox = Gtk.FlowBox()
        self._bat_flowbox.set_max_children_per_line(4)
        self._bat_flowbox.set_min_children_per_line(2)
        self._bat_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self._bat_flowbox.set_column_spacing(6)
        self._bat_flowbox.set_row_spacing(6)
        self._bat_flowbox.set_margin_top(6)
        self._bat_flowbox.set_margin_bottom(6)
        self._bat_flowbox.set_homogeneous(True)

        scroll.add(self._bat_flowbox)

        # Área de contenido: spinner primero, luego scroll
        self._bat_content_area = Gtk.Stack()
        self._bat_content_area.add_named(spinner, "spinner")
        self._bat_content_area.add_named(scroll, "baterias")
        self._bat_content_area.set_visible_child_name("spinner")
        vbox.pack_start(self._bat_content_area, True, True, 0)

        # Label resumen abajo
        self._bat_resumen = Gtk.Label()
        self._bat_resumen.set_halign(Gtk.Align.START)
        vbox.pack_start(self._bat_resumen, False, False, 4)

        def cargar():
            datos = self.obtener_baterias()
            GLib.idle_add(lambda: self.mostrar_baterias(datos))

        btn_refresh.connect("clicked", lambda w: threading.Thread(target=cargar, daemon=True).start())

        dialog.show_all()
        threading.Thread(target=cargar, daemon=True).start()

    def obtener_baterias(self):
        """Consulta /clip/v2/resource/device_power y retorna lista de dispositivos con batería"""
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/device_power"
            response = requests.get(url, headers=self.headers, verify=False, timeout=8)
            if response.status_code != 200:
                return []

            data = response.json()
            resultados = []

            # Construir mapa device_id → nombre
            nombres = {}
            url_dev = f"https://{self.bridge_ip}/clip/v2/resource/device"
            resp_dev = requests.get(url_dev, headers=self.headers, verify=False, timeout=8)
            if resp_dev.status_code == 200:
                for dev in resp_dev.json().get('data', []):
                    nombres[dev['id']] = dev.get('metadata', {}).get('name', 'Dispositivo')
                    # También mapear los services del device para resolver owner
                    for svc in dev.get('services', []):
                        nombres[svc['rid']] = dev.get('metadata', {}).get('name', 'Dispositivo')

            for item in data.get('data', []):
                power = item.get('power_state', {})
                nivel = power.get('battery_level')
                estado = power.get('battery_state', '')
                owner = item.get('owner', {}).get('rid', '')

                if nivel is None:
                    continue

                nombre = nombres.get(owner, nombres.get(item.get('id', ''), 'Dispositivo'))

                # Detectar tipo por servicios del device
                tipo = 'Desconocido'
                url_d = f"https://{self.bridge_ip}/clip/v2/resource/device/{owner}"
                try:
                    rd = requests.get(url_d, headers=self.headers, verify=False, timeout=5)
                    if rd.status_code == 200:
                        svcs = rd.json().get('data', [{}])[0].get('services', [])
                        rtypes = [s.get('rtype', '') for s in svcs]
                        if 'motion' in rtypes:
                            tipo = '📡 Sensor de movimiento'
                        elif 'temperature' in rtypes:
                            tipo = '🌡️ Sensor temperatura'
                        elif 'button' in rtypes or 'relative_rotary' in rtypes:
                            tipo = '🔘 Switch / Dimmer'
                        elif 'light' in rtypes:
                            tipo = '💡 Luz'
                        else:
                            tipo = '📦 ' + ', '.join(set(rtypes))
                except:
                    pass

                resultados.append({
                    'nombre': nombre,
                    'nivel': nivel,
                    'estado': estado,
                    'tipo': tipo,
                })

            # Ordenar: baja primero
            resultados.sort(key=lambda x: x['nivel'])

            # Actualizar ícono del botón según el peor nivel
            if resultados:
                peor = resultados[0]['nivel']
                if peor < 5:
                    color = (0.9, 0.15, 0.15)   # rojo
                elif peor < 40:
                    color = (0.95, 0.75, 0.1)   # amarillo
                else:
                    color = (0.2, 0.8, 0.2)     # verde

                def _update_icon(c=color, p=peor):
                    self._bat_color = c
                    self._bat_nivel = p
                    self._actualizar_imagen_bateria()
                GLib.idle_add(_update_icon)

            return resultados

        except Exception as e:
            print(f"Error obteniendo baterías: {e}")
            return []

    def mostrar_baterias(self, datos):
        """Actualiza el FlowBox con las tarjetas de batería"""
        for child in self._bat_flowbox.get_children():
            self._bat_flowbox.remove(child)

        if not datos:
            lbl = Gtk.Label()
            lbl.set_markup("<span foreground='gray'>No se encontraron dispositivos con batería</span>")
            lbl.set_margin_top(40)
            self._bat_flowbox.add(lbl)
        else:
            for d in datos:
                card = self._crear_tarjeta_bateria(d)
                self._bat_flowbox.add(card)

            bajas = [d for d in datos if d['nivel'] < 20]
            medias = [d for d in datos if 20 <= d['nivel'] < 50]
            resumen = f"<b>{len(datos)}</b> dispositivos"
            if bajas:
                resumen += f" · <span foreground='#ff6b6b'><b>{len(bajas)} con batería baja</b></span>"
            if medias:
                resumen += f" · <span foreground='#ffd93d'>{len(medias)} con batería media</span>"
            self._bat_resumen.set_markup(resumen)

        self._bat_content_area.set_visible_child_name("baterias")
        self._bat_flowbox.show_all()

    def _crear_tarjeta_bateria(self, datos):
        """Crea una tarjeta para un dispositivo con batería"""
        nivel = datos['nivel']

        if nivel < 5:
            css_class = "bateria-card-baja"
            color = (0.9, 0.15, 0.15)
        elif nivel < 40:
            css_class = "bateria-card-media"
            color = (0.95, 0.75, 0.1)
        else:
            css_class = "bateria-card-ok"
            color = (0.2, 0.8, 0.2)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card.get_style_context().add_class("bateria-card")
        card.get_style_context().add_class(css_class)
        card.set_size_request(150, -1)

        # Fila superior: ícono Cairo + nivel
        fila_nivel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        fila_nivel.set_halign(Gtk.Align.CENTER)

        icono = Gtk.Image()
        icono.set_size_request(38, 22)
        try:
            pixbuf = self._render_battery_pixbuf(38, 22, color, nivel)
            icono.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"Error ícono tarjeta: {e}")

        lbl_nivel = Gtk.Label()
        lbl_nivel.set_markup(f"<span size='x-large' weight='bold'>{nivel}%</span>")
        lbl_nivel.get_style_context().add_class("bateria-nivel")
        fila_nivel.pack_start(icono, False, False, 0)
        fila_nivel.pack_start(lbl_nivel, False, False, 0)
        card.pack_start(fila_nivel, False, False, 2)

        # Barra de progreso
        barra = Gtk.ProgressBar()
        barra.set_fraction(nivel / 100)
        barra.set_margin_start(8)
        barra.set_margin_end(8)
        card.pack_start(barra, False, False, 0)

        # Nombre del dispositivo
        lbl_nombre = Gtk.Label()
        lbl_nombre.set_markup(f"<b>{GLib.markup_escape_text(datos['nombre'])}</b>")
        lbl_nombre.get_style_context().add_class("bateria-nombre")
        lbl_nombre.set_ellipsize(3)
        lbl_nombre.set_max_width_chars(18)
        lbl_nombre.set_halign(Gtk.Align.CENTER)
        card.pack_start(lbl_nombre, False, False, 0)

        # Tipo de dispositivo
        lbl_tipo = Gtk.Label(label=datos['tipo'])
        lbl_tipo.get_style_context().add_class("bateria-tipo")
        lbl_tipo.set_halign(Gtk.Align.CENTER)
        card.pack_start(lbl_tipo, False, False, 2)

        return card



    def on_update_interval_changed(self, widget):
        """Cambia el intervalo de actualización de sensores"""
        minutos = int(widget.get_value())
        self.update_interval = minutos * 60
        self.config["update_interval"] = self.update_interval
        self.guardar_configuracion()
        
        # Reiniciar el timer si estamos conectados
        if self.bridge_ip and self.api_key:
            if self.update_timer is not None:
                try:
                    GLib.source_remove(self.update_timer)
                except:
                    pass
                self.update_timer = None
            
            self.update_timer = GLib.timeout_add_seconds(self.update_interval, self.actualizar_sensores_periodicamente)
            print(f"Intervalo de actualización cambiado a {minutos} minutos")
    
    def on_buscar_bridge_clicked(self, widget):
        """Inicia la búsqueda del bridge Hue en la red"""
        self.label_estado.set_markup("<span foreground='orange'>🔍 Buscando bridge en la red WiFi...</span>")
        self.btn_conectar.set_sensitive(False)
        self.btn_buscar_bridge.set_sensitive(False)
        self.spinner.start()
        threading.Thread(target=self._buscar_bridges_thread, daemon=True).start()

    def _buscar_bridges_thread(self):
        """Hilo de búsqueda: primero API de Philips, luego escaneo local"""
        import socket
        import ipaddress
        from concurrent.futures import ThreadPoolExecutor

        bridges = []

        # Método 1: API N-UPnP de Philips Hue (requiere internet)
        try:
            resp = requests.get("https://discovery.meethue.com/", timeout=5, verify=True)
            if resp.status_code == 200:
                for entry in resp.json():
                    ip = entry.get("internalipaddress")
                    if ip and ip not in bridges:
                        bridges.append(ip)
        except Exception as e:
            print(f"discovery.meethue.com no disponible: {e}")

        # Método 2: Escaneo local /24 si el método 1 no dio resultados
        if not bridges:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()

                network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
                hosts = [str(h) for h in network.hosts()]

                def check_host(ip_str):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.4)
                        if sock.connect_ex((ip_str, 443)) == 0:
                            sock.close()
                            try:
                                r = requests.get(
                                    f"https://{ip_str}/api/0/config",
                                    verify=False, timeout=2
                                )
                                if r.status_code == 200 and "bridgeid" in r.text:
                                    return ip_str
                            except Exception:
                                pass
                        else:
                            sock.close()
                    except Exception:
                        pass
                    return None

                with ThreadPoolExecutor(max_workers=40) as executor:
                    results = list(executor.map(check_host, hosts))

                bridges = [ip for ip in results if ip is not None]
            except Exception as e:
                print(f"Error en escaneo local: {e}")

        GLib.idle_add(self._mostrar_bridges_encontrados, bridges)

    def _mostrar_bridges_encontrados(self, bridges):
        """Muestra los bridges encontrados y permite seleccionar uno"""
        self.btn_conectar.set_sensitive(True)
        self.btn_buscar_bridge.set_sensitive(True)
        self.spinner.stop()

        if not bridges:
            self.label_estado.set_markup(
                "<span foreground='red'>❌ No se encontró ningún bridge Hue en la red</span>"
            )
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="No se encontró ningún bridge Hue"
            )
            dialog.format_secondary_text(
                "No se detectó ningún bridge Philips Hue en la red WiFi.\n\n"
                "Verifica que:\n"
                "• El bridge esté encendido y conectado al router\n"
                "• Tu PC esté en la misma red WiFi\n"
                "• El LED del bridge esté azul sólido\n\n"
                "También puedes ingresar la IP manualmente."
            )
            dialog.run()
            dialog.destroy()
            return

        if len(bridges) == 1:
            self.ip_entry.set_text(bridges[0])
            self.label_estado.set_markup(
                f"<span foreground='green'>✅ Bridge encontrado: {bridges[0]}</span>"
            )
        else:
            dialog = Gtk.Dialog(title="Bridges Hue encontrados", transient_for=self)
            dialog.set_default_size(320, 180)
            content = dialog.get_content_area()
            content.set_spacing(8)
            content.set_margin_top(12)
            content.set_margin_bottom(10)
            content.set_margin_start(14)
            content.set_margin_end(14)

            lbl = Gtk.Label()
            lbl.set_markup("<b>Se encontraron varios bridges. Selecciona uno:</b>")
            lbl.set_halign(Gtk.Align.START)
            content.add(lbl)

            selected = [None]

            def seleccionar(w, ip):
                selected[0] = ip
                dialog.response(Gtk.ResponseType.OK)

            for ip in bridges:
                btn = Gtk.Button(label=f"🌉  {ip}")
                btn.connect("clicked", seleccionar, ip)
                content.add(btn)

            dialog.show_all()
            dialog.run()
            dialog.destroy()

            if selected[0]:
                self.ip_entry.set_text(selected[0])
                self.label_estado.set_markup(
                    f"<span foreground='green'>✅ Bridge seleccionado: {selected[0]}</span>"
                )

    def on_conectar_clicked(self, widget):
        """Maneja el click en el botón conectar"""
        ip = self.ip_entry.get_text().strip()
        
        if not ip:
            self.on_buscar_bridge_clicked(None)
            return
        
        self.bridge_ip = ip
        self.config["bridge_ip"] = ip
        self.guardar_configuracion()
        
        # Si ya tenemos API key guardada, intentar usarla
        if self.config.get("api_key"):
            self.api_key = self.config["api_key"]
            self.headers = {"hue-application-key": self.api_key, "Content-Type": "application/json"}
            self.label_estado.set_markup("<span foreground='orange'>🔄 Conectando...</span>")
            self.btn_conectar.set_sensitive(False)
            self.spinner.start()
            threading.Thread(target=self.probar_conexion, daemon=True).start()
        else:
            # No hay API key, solicitar registro
            self.solicitar_registro()
    
    def probar_conexion(self):
        """Prueba la conexión con la API key guardada"""
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/device"
            response = requests.get(url, headers=self.headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                GLib.idle_add(self.conexion_exitosa)
            else:
                GLib.idle_add(self.solicitar_registro)
        except Exception as e:
            print(f"Error probando conexión: {e}")
            GLib.idle_add(self.solicitar_registro)
    
    def solicitar_registro(self):
        """Solicita al usuario que presione el botón del puente"""
        self.label_estado.set_markup("<span foreground='orange'>⚠️ Presiona el botón físico del puente Hue</span>")
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text="Registro en el puente Hue"
        )
        dialog.format_secondary_text(
            "Para conectar la aplicación, debes presionar el botón físico "
            "del puente Philips Hue y luego hacer clic en 'Registrar'.\n\n"
            "Esta operación solo se realiza una vez."
        )
        
        btn_registrar = dialog.add_button("🔘 Ya presioné el botón, Registrar", Gtk.ResponseType.OK)
        btn_cancelar = dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        
        btn_registrar.get_style_context().add_class("btn-encender")
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
            self.spinner.start()
            self.label_estado.set_markup("<span foreground='orange'>🔄 Registrando aplicación...</span>")
            threading.Thread(target=self.registrar_aplicacion, daemon=True).start()
        else:
            dialog.destroy()
            self.btn_conectar.set_sensitive(True)
            self.spinner.stop()
            self.label_estado.set_markup("<span foreground='red'>❌ Registro cancelado</span>")
    
    def registrar_aplicacion(self):
        """Registra la aplicación en el puente Hue (obtiene api_key y entertainment key en un solo paso)"""
        try:
            app_name = self.config.get("app_name", "hue_controller_linux")
            url = f"https://{self.bridge_ip}/api"
            data = {"devicetype": app_name, "generateclientkey": True}

            response = requests.post(url, json=data, verify=False, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if 'success' in result[0]:
                    success = result[0]['success']
                    self.api_key = success['username']
                    self.headers = {"hue-application-key": self.api_key, "Content-Type": "application/json"}

                    self.config["api_key"] = self.api_key
                    self.config["ent_username"] = success['username']
                    self.config["ent_clientkey"] = success.get('clientkey', '')
                    self.guardar_configuracion()

                    GLib.idle_add(self.conexion_exitosa)
                elif 'error' in result[0]:
                    error_type = result[0]['error']['type']
                    if error_type == 101:
                        GLib.idle_add(self.mostrar_error_registro, "No se detectó el botón presionado. Asegúrate de presionar el botón físico del puente antes de registrar.")
                    else:
                        GLib.idle_add(self.mostrar_error_registro, f"Error: {result[0]['error']['description']}")
            else:
                GLib.idle_add(self.mostrar_error_registro, f"Error HTTP: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            GLib.idle_add(self.mostrar_error_registro, "No se pudo conectar al puente. Verifica la IP.")
        except Exception as e:
            GLib.idle_add(self.mostrar_error_registro, str(e))
    
    def mostrar_error_registro(self, mensaje):
        """Muestra error de registro"""
        self.spinner.stop()
        self.btn_conectar.set_sensitive(True)
        self.label_estado.set_markup(f"<span foreground='red'>❌ Error: {mensaje}</span>")
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error de registro"
        )
        dialog.format_secondary_text(mensaje)
        dialog.run()
        dialog.destroy()
    
    def conexion_exitosa(self):
        """Maneja la conexión exitosa"""
        self.label_estado.set_markup("<span foreground='green'>✅ Conectado al puente</span>")
        self.btn_conectar.set_sensitive(False)
        self.spinner.stop()
        self.spinner.hide()
        
        # Detener timer existente
        if self.update_timer is not None:
            try:
                GLib.source_remove(self.update_timer)
            except:
                pass
            self.update_timer = None
        
        threading.Thread(target=self.cargar_todos_los_datos, daemon=True).start()
        return False
    
    def cargar_todos_los_datos(self):
        """Carga todos los datos usando API v2"""
        self.cargar_recursos()
        GLib.idle_add(self.iniciar_actualizacion_periodica)
    
    def cargar_recursos(self):
        """Carga los recursos de la API v2"""
        try:
            # Cargar rooms (habitaciones)
            url = f"https://{self.bridge_ip}/clip/v2/resource/room"
            response = requests.get(url, headers=self.headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                self.rooms = {}
                for item in data.get('data', []):
                    room_id = item.get('id')
                    room_name = item.get('metadata', {}).get('name', 'Sin nombre')
                    self.rooms[room_id] = {
                        'id': room_id,
                        'name': room_name,
                        'type': 'Room',
                        'icono': '🏠',
                        'children': item.get('children', [])
                    }
                    print(f"Habitación encontrada: {room_name}")
            
            # Cargar dispositivos (luces) con detección de color
            url = f"https://{self.bridge_ip}/clip/v2/resource/device"
            response = requests.get(url, headers=self.headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', []):
                    device_id = item.get('id')
                    device_name = item.get('metadata', {}).get('name', 'Sin nombre')
                    
                    services = item.get('services', [])
                    for service in services:
                        if service.get('rtype') == 'light':
                            self.devices[device_id] = {
                                'id': device_id,
                                'name': device_name,
                                'service_id': service.get('rid'),
                                'on': False,
                                'brightness': 0,
                                'has_color': False,
                                'color_xy': [0.5, 0.5]
                            }
                            print(f"Dispositivo encontrado: {device_name}")
            
            # Cargar servicios de luz (estado actual y capacidad de color)
            url = f"https://{self.bridge_ip}/clip/v2/resource/light"
            response = requests.get(url, headers=self.headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', []):
                    light_id = item.get('id')
                    for device_id, device in self.devices.items():
                        if device.get('service_id') == light_id:
                            device['on'] = item.get('on', {}).get('on', False)
                            device['brightness'] = item.get('dimming', {}).get('brightness', 0)
                            # Detectar si la luz soporta color
                            color_info = item.get('color', {})
                            if color_info and ('xy' in color_info or 'gamut' in color_info):
                                device['has_color'] = True
                                if 'xy' in color_info:
                                    device['color_xy'] = color_info.get('xy', [0.5, 0.5])
                            print(f"Luz {device['name']} - Color: {device['has_color']}")
            
            # Cargar escenas
            self.cargar_escenas()
            
            # Cargar sensores de temperatura
            self.cargar_sensores()
            
            # Asignar sensores a habitaciones
            self.asignar_sensores_a_habitaciones()
            
            GLib.idle_add(self.actualizar_interfaz)

            # Actualizar ícono de batería en segundo plano
            threading.Thread(target=lambda: self.obtener_baterias(), daemon=True).start()

        except Exception as e:
            print(f"Error cargando recursos: {e}")
            import traceback
            traceback.print_exc()
    
    def cargar_escenas(self):
        """Carga las escenas del bridge"""
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/scene"
            response = requests.get(url, headers=self.headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                self.scenes = {}
                self.scenes_by_room = {}
                
                for item in data.get('data', []):
                    scene_id = item.get('id')
                    scene_name = item.get('metadata', {}).get('name', 'Sin nombre')
                    scene_group = item.get('group', {}).get('rid', '')
                    
                    # Buscar a qué habitación pertenece la escena
                    room_name = "Sin habitación"
                    for room_id, room in self.rooms.items():
                        if room_id == scene_group:
                            room_name = room['name']
                            break
                    
                    self.scenes[scene_id] = {
                        'id': scene_id,
                        'name': scene_name,
                        'group_rid': scene_group,
                        'room_name': room_name,
                        'icon': self.obtener_icono_escena(scene_name)
                    }
                    
                    # Agrupar escenas por habitación
                    if room_name not in self.scenes_by_room:
                        self.scenes_by_room[room_name] = []
                    self.scenes_by_room[room_name].append(self.scenes[scene_id])
                    
                    print(f"Escena encontrada: {scene_name} - Habitación: {room_name}")
                    
        except Exception as e:
            print(f"Error cargando escenas: {e}")
    
    def obtener_icono_escena(self, nombre_escena):
        """Asigna un icono según el nombre de la escena"""
        nombre_lower = nombre_escena.lower()
        
        if 'relax' in nombre_lower or 'descanso' in nombre_lower:
            return "😌"
        elif 'read' in nombre_lower or 'lectura' in nombre_lower or 'leer' in nombre_lower:
            return "📚"
        elif 'night' in nombre_lower or 'noche' in nombre_lower:
            return "🌙"
        elif 'morning' in nombre_lower or 'mañana' in nombre_lower:
            return "🌅"
        elif 'day' in nombre_lower or 'dia' in nombre_lower:
            return "☀️"
        elif 'party' in nombre_lower or 'fiesta' in nombre_lower:
            return "🎉"
        elif 'focus' in nombre_lower or 'concentrar' in nombre_lower:
            return "🎯"
        elif 'sunset' in nombre_lower or 'atardecer' in nombre_lower:
            return "🌇"
        elif 'forest' in nombre_lower or 'bosque' in nombre_lower:
            return "🌲"
        elif 'ocean' in nombre_lower or 'oceano' in nombre_lower:
            return "🌊"
        elif 'energize' in nombre_lower or 'energia' in nombre_lower:
            return "⚡"
        elif 'romantic' in nombre_lower or 'romance' in nombre_lower:
            return "❤️"
        elif 'arctic' in nombre_lower or 'polar' in nombre_lower:
            return "❄️"
        elif 'tropical' in nombre_lower:
            return "🏝️"
        else:
            return "🎨"
    
    def cargar_sensores(self):
        """Carga los sensores de temperatura del bridge"""
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/temperature"
            response = requests.get(url, headers=self.headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                self.sensors = {}
                
                for item in data.get('data', []):
                    sensor_id = item.get('id')
                    sensor_owner = item.get('owner', {})
                    owner_rid = sensor_owner.get('rid', '')
                    
                    temperature_data = item.get('temperature', {})
                    temperature_celsius = temperature_data.get('temperature', 0)
                    
                    last_changed = None
                    temperature_report = temperature_data.get('temperature_report', {})
                    if temperature_report:
                        changed_str = temperature_report.get('changed', '')
                        if changed_str:
                            try:
                                last_changed = datetime.datetime.fromisoformat(changed_str.replace('Z', '+00:00'))
                            except:
                                last_changed = datetime.datetime.now()
                    
                    device_name = "Sensor de temperatura"
                    try:
                        if owner_rid:
                            url_device = f"https://{self.bridge_ip}/clip/v2/resource/device/{owner_rid}"
                            device_resp = requests.get(url_device, headers=self.headers, verify=False)
                            if device_resp.status_code == 200:
                                device_data = device_resp.json()
                                device_name = device_data.get('data', [{}])[0].get('metadata', {}).get('name', 'Sensor')
                    except:
                        pass
                    
                    self.sensors[sensor_id] = {
                        'id': sensor_id,
                        'name': device_name,
                        'owner_rid': owner_rid,
                        'temperature': temperature_celsius,
                        'ubicacion': 'Sin ubicación',
                        'last_updated': last_changed or datetime.datetime.now()
                    }
                    print(f"Sensor encontrado: {device_name} - Temperatura: {temperature_celsius:.1f}°C")
                    
        except Exception as e:
            print(f"Error en cargar_sensores: {e}")
            import traceback
            traceback.print_exc()
    
    def asignar_sensores_a_habitaciones(self):
        """Asigna los sensores a las habitaciones correspondientes"""
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/device"
            response = requests.get(url, headers=self.headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                device_to_room = {}
                
                for room_id, room in self.rooms.items():
                    for child in room.get('children', []):
                        child_rid = child.get('rid')
                        device_to_room[child_rid] = room['name']
                
                for sensor_id, sensor in self.sensors.items():
                    owner_rid = sensor.get('owner_rid')
                    if owner_rid in device_to_room:
                        sensor['ubicacion'] = device_to_room[owner_rid]
                    else:
                        sensor_name = sensor['name'].lower()
                        for room_id, room in self.rooms.items():
                            room_name = room['name'].lower()
                            if room_name in sensor_name or sensor_name in room_name:
                                sensor['ubicacion'] = room['name']
                                break
                    
                    print(f"Sensor asignado a: {sensor['ubicacion']} - {sensor['temperature']:.1f}°C")
                    
        except Exception as e:
            print(f"Error asignando sensores: {e}")
    
    def actualizar_interfaz(self):
        """Actualiza toda la interfaz"""
        self.actualizar_interfaz_grupos()
        self.actualizar_interfaz_sensores()
    
    def actualizar_interfaz_grupos(self):
        """Actualiza la lista de habitaciones"""
        for child in self.lista_habitaciones.get_children():
            self.lista_habitaciones.remove(child)
        
        if not self.rooms:
            label_no_grupos = Gtk.Label()
            label_no_grupos.set_markup("<span foreground='orange'>⚠️ No se encontraron habitaciones</span>")
            self.lista_habitaciones.pack_start(label_no_grupos, False, False, 0)
            return
        
        self.botones_habitacion = {}
        self.switches_habitacion = {}
        
        for room_id, room in self.rooms.items():
            luces_room = []
            for child in room.get('children', []):
                child_rid = child.get('rid')
                if child_rid in self.devices:
                    luces_room.append(self.devices[child_rid])
            
            if not luces_room:
                continue
            
            contenedor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            contenedor.set_margin_bottom(3)
            contenedor.get_style_context().add_class("habitacion-item")
            
            btn_habitacion = Gtk.Button(label=f"{room['icono']} {room['name']} ({len(luces_room)} luces)")
            btn_habitacion.connect("clicked", self.on_habitacion_seleccionada, room_id, room['name'], luces_room)
            btn_habitacion.set_halign(Gtk.Align.START)
            btn_habitacion.set_valign(Gtk.Align.CENTER)
            btn_habitacion.set_hexpand(True)
            
            alguna_encendida = any(luz.get('on', False) for luz in luces_room)
            switch = Gtk.Switch()
            switch.set_active(alguna_encendida)
            switch.set_halign(Gtk.Align.END)
            switch.set_valign(Gtk.Align.CENTER)
            switch.set_tooltip_text(f"Encender/Apagar todas las luces de {room['name']}")
            switch.connect("notify::active", self.on_habitacion_switch_toggled, room_id, luces_room)
            
            contenedor.pack_start(btn_habitacion, True, True, 0)
            contenedor.pack_start(switch, False, False, 0)
            
            self.lista_habitaciones.pack_start(contenedor, False, False, 0)
            
            self.botones_habitacion[room_id] = btn_habitacion
            self.switches_habitacion[room_id] = switch
        
        self.lista_habitaciones.show_all()
    
    def on_habitacion_switch_toggled(self, switch, gparam, room_id, luces_room):
        """Maneja el cambio del switch de la habitación"""
        if self._actualizando_switch_habitacion:
            return
        nuevo_estado = switch.get_active()

        # Actualizar la UI inmediatamente (hilo principal)
        switch.handler_block_by_func(self.on_habitacion_switch_toggled)
        try:
            for luz in luces_room:
                luz['on'] = nuevo_estado

                if luz['id'] in self.switches_luces:
                    luz_switch = self.switches_luces[luz['id']]
                    luz_switch.handler_block_by_func(self.on_luz_switch_toggled)
                    luz_switch.set_active(nuevo_estado)
                    luz_switch.handler_unblock_by_func(self.on_luz_switch_toggled)

                if luz['id'] in self.sliders_luces:
                    slider = self.sliders_luces[luz['id']]
                    slider.handler_block_by_func(self.on_brillo_changed)
                    if nuevo_estado:
                        brillo = luz.get('brightness_real', luz.get('brightness', 50))
                        if brillo == 0:
                            brillo = 50
                        slider.set_value(brillo)
                        slider.set_sensitive(True)
                    else:
                        brillo_actual = luz.get('brightness', 0)
                        if brillo_actual > 0:
                            luz['brightness_real'] = brillo_actual
                        slider.set_value(0)
                        slider.set_sensitive(False)
                    slider.handler_unblock_by_func(self.on_brillo_changed)
        finally:
            switch.handler_unblock_by_func(self.on_habitacion_switch_toggled)

        # Enviar comandos HTTP en un thread separado para no bloquear la UI
        def enviar_comandos():
            errores = []
            for luz in luces_room:
                try:
                    self.controlar_luz(luz, nuevo_estado)
                except Exception as e:
                    errores.append(luz.get('name', '?'))
                    print(f"Error controlando {luz.get('name')}: {e}")
            if errores:
                GLib.idle_add(
                    self.mostrar_error,
                    f"No se pudieron controlar: {', '.join(errores)}"
                )

        threading.Thread(target=enviar_comandos, daemon=True).start()
    
    def controlar_luz(self, luz, encender):
        """Controla una luz individual"""
        try:
            service_id = luz.get('service_id')
            if not service_id:
                return
            
            url = f"https://{self.bridge_ip}/clip/v2/resource/light/{service_id}"
            data = {"on": {"on": encender}}
            
            if encender and luz.get('brightness', 0) > 0:
                data["dimming"] = {"brightness": luz.get('brightness', 50)}
            
            requests.put(url, headers=self.headers, json=data, verify=False, timeout=5)
            luz['on'] = encender
            
        except Exception as e:
            print(f"Error controlando luz {luz.get('name')}: {e}")
    
    def cambiar_brillo(self, luz, porcentaje):
        """Cambia el brillo de una luz"""
        try:
            service_id = luz.get('service_id')
            if not service_id:
                return
            
            url = f"https://{self.bridge_ip}/clip/v2/resource/light/{service_id}"
            data = {"dimming": {"brightness": porcentaje}}
            
            if not luz.get('on'):
                data["on"] = {"on": True}
            
            requests.put(url, headers=self.headers, json=data, verify=False, timeout=5)
            luz['brightness'] = porcentaje
            if not luz.get('on'):
                luz['on'] = True
            
        except Exception as e:
            print(f"Error cambiando brillo: {e}")
    
    def cambiar_color(self, luz, color_rgb):
        """Cambia el color de una luz RGB"""
        try:
            service_id = luz.get('service_id')
            if not service_id:
                return
            
            # Convertir RGB a xy (formato que entiende Hue)
            x, y = self.rgb_to_xy(color_rgb[0], color_rgb[1], color_rgb[2])
            
            url = f"https://{self.bridge_ip}/clip/v2/resource/light/{service_id}"
            data = {
                "color": {"xy": {"x": x, "y": y}}
            }
            
            if not luz.get('on'):
                data["on"] = {"on": True}
            
            requests.put(url, headers=self.headers, json=data, verify=False, timeout=5)
            luz['color_xy'] = [x, y]
            if not luz.get('on'):
                luz['on'] = True
                if luz['id'] in self.switches_luces:
                    self.switches_luces[luz['id']].set_active(True)
            
            print(f"Color cambiado para {luz['name']}")
            
        except Exception as e:
            print(f"Error cambiando color: {e}")
    
    def rgb_to_xy(self, r, g, b):
        """Convierte RGB a coordenadas xy para Hue"""
        # Normalizar RGB
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
        
        # Aplicar corrección gamma
        r = self.gamma_correction(r)
        g = self.gamma_correction(g)
        b = self.gamma_correction(b)
        
        # Convertir a XYZ
        X = r * 0.664511 + g * 0.154324 + b * 0.162028
        Y = r * 0.283881 + g * 0.668433 + b * 0.047685
        Z = r * 0.000088 + g * 0.072310 + b * 0.986039
        
        # Calcular xy
        if X + Y + Z == 0:
            return (0.0, 0.0)
        
        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)
        
        return (x, y)
    
    def gamma_correction(self, value):
        """Aplica corrección gamma"""
        if value > 0.04045:
            return ((value + 0.055) / (1.0 + 0.055)) ** 2.4
        else:
            return value / 12.92
    
    def actualizar_interfaz_sensores(self):
        """Actualiza la interfaz de sensores"""
        for child in self.sensores_container.get_children():
            self.sensores_container.remove(child)
        
        if not self.sensors:
            label_no_sensores = Gtk.Label()
            label_no_sensores.set_markup("<span foreground='gray'>📭 No se encontraron sensores de temperatura</span>")
            label_no_sensores.set_margin_top(20)
            self.sensores_container.pack_start(label_no_sensores, False, False, 0)
        else:
            sensores_validos = []
            for sensor in self.sensors.values():
                if -20 < sensor['temperature'] < 60:
                    sensores_validos.append(sensor)
            
            if not sensores_validos:
                label_no_sensores = Gtk.Label()
                label_no_sensores.set_markup("<span foreground='gray'>📭 No hay datos de temperatura válidos</span>")
                label_no_sensores.set_margin_top(20)
                self.sensores_container.pack_start(label_no_sensores, False, False, 0)
            else:
                sensores_ordenados = sorted(sensores_validos, key=lambda x: x['ubicacion'])
                
                for sensor_data in sensores_ordenados:
                    self.crear_tarjeta_sensor(sensor_data)
        
        self.sensores_container.show_all()
    
    def crear_tarjeta_sensor(self, sensor_data):
        """Crea una tarjeta visual para un sensor"""
        # Layout horizontal: temperatura grande a la izquierda, info a la derecha
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        card.get_style_context().add_class("sensor-card")
        card.set_size_request(-1, 70)

        # Temperatura grande
        temp = Gtk.Label()
        temp.set_markup(f"<span size='xx-large' weight='bold'>{sensor_data['temperature']:.1f}°C</span>")
        temp.get_style_context().add_class("sensor-temperatura")
        temp.set_valign(Gtk.Align.CENTER)
        temp.set_margin_start(5)
        temp.set_margin_end(5)
        card.pack_start(temp, False, False, 0)

        # Separador vertical
        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        sep.set_margin_top(8)
        sep.set_margin_bottom(8)
        card.pack_start(sep, False, False, 0)

        # Info: ubicación y hora
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info_box.set_valign(Gtk.Align.CENTER)
        info_box.set_margin_start(5)
        info_box.set_margin_end(8)

        ubicacion_texto = sensor_data['ubicacion'] if sensor_data['ubicacion'] != 'Sin ubicación' else 'Desconocida'
        ubicacion = Gtk.Label()
        ubicacion.set_markup(f"<span weight='bold'>📍 {ubicacion_texto}</span>")
        ubicacion.get_style_context().add_class("sensor-ubicacion")
        ubicacion.set_xalign(0)
        ubicacion.set_ellipsize(3)  # PANGO_ELLIPSIZE_END

        last_up = Gtk.Label()
        last_up.set_markup(f"<span size='small' foreground='#cccccc'>🕐 {sensor_data['last_updated'].strftime('%H:%M:%S')}</span>")
        last_up.get_style_context().add_class("sensor-updated")
        last_up.set_xalign(0)

        info_box.pack_start(ubicacion, False, False, 0)
        info_box.pack_start(last_up, False, False, 0)
        card.pack_start(info_box, True, True, 0)

        self.sensores_container.pack_start(card, False, False, 0)
    
    def on_habitacion_seleccionada(self, widget, room_id, nombre_room, luces_room):
        """Muestra los controles de la habitación seleccionada"""
        self.habitacion_actual = room_id
        room = self.rooms.get(room_id, {})
        
        self.nombre_habitacion_label.set_markup(
            f"<span size='x-large' weight='bold'>{room.get('icono', '🏠')} {nombre_room}</span>\n"
            f"<span size='small'>Habitación con {len(luces_room)} luces</span>"
        )
        
        # Cargar escenas para esta habitación
        self.cargar_escenas_para_habitacion(nombre_room)
        
        # Cargar luces
        self.cargar_luces_habitacion(luces_room)
    
    def cargar_escenas_para_habitacion(self, nombre_habitacion):
        """Carga las escenas para la habitación seleccionada"""
        for child in self.escenas_container.get_children():
            self.escenas_container.remove(child)
        
        if nombre_habitacion in self.scenes_by_room and self.scenes_by_room[nombre_habitacion]:
            escenas = self.scenes_by_room[nombre_habitacion]
            
            for escena in escenas:
                self.crear_boton_escena(escena)
            
            self.escenas_frame.show()
        else:
            self.escenas_frame.hide()
        
        self.escenas_container.show_all()
    
    def crear_boton_escena(self, escena):
        """Crea un botón cuadrado para una escena"""
        contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        contenedor.get_style_context().add_class("escena-boton")
        contenedor.set_size_request(90, 90)
        
        icono = Gtk.Label()
        icono.set_markup(f"<span size='x-large'>{escena['icon']}</span>")
        icono.get_style_context().add_class("escena-icono")
        
        nombre = Gtk.Label()
        nombre_texto = escena['name'][:15] + "..." if len(escena['name']) > 15 else escena['name']
        nombre.set_markup(f"<span size='small'>{nombre_texto}</span>")
        nombre.get_style_context().add_class("escena-nombre")
        nombre.set_line_wrap(True)
        nombre.set_max_width_chars(12)
        
        contenedor.pack_start(icono, True, True, 0)
        contenedor.pack_start(nombre, False, False, 0)
        
        btn = Gtk.Button()
        btn.add(contenedor)
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.set_tooltip_text(f"Aplicar escena: {escena['name']}")
        btn.connect("clicked", self.on_escena_clicked, escena['id'])
        
        self.escenas_container.pack_start(btn, False, False, 0)
    
    def on_escena_clicked(self, widget, scene_id):
        """Aplica una escena seleccionada"""
        try:
            scene = self.scenes.get(scene_id)
            if not scene:
                return
            
            group_rid = scene.get('group_rid')
            if not group_rid:
                return
            
            # Aplicar la escena
            url = f"https://{self.bridge_ip}/clip/v2/resource/scene/{scene_id}/actions"
            
            get_url = f"https://{self.bridge_ip}/clip/v2/resource/scene/{scene_id}"
            response = requests.get(get_url, headers=self.headers, verify=False)
            
            if response.status_code == 200:
                scene_data = response.json()
                actions = scene_data.get('data', [{}])[0].get('actions', [])
                
                for action in actions:
                    target = action.get('target', {})
                    target_rid = target.get('rid')
                    action_data = action.get('action', {})
                    
                    if target_rid:
                        put_url = f"https://{self.bridge_ip}/clip/v2/resource/light/{target_rid}"
                        requests.put(put_url, headers=self.headers, json=action_data, verify=False)
                
                print(f"Escena aplicada: {scene['name']}")
                
                GLib.timeout_add(500, self.actualizar_despues_escena)
            
        except Exception as e:
            self.mostrar_error(f"Error al aplicar escena: {e}")
    
    def actualizar_despues_escena(self):
        """Actualiza la interfaz después de aplicar una escena"""
        threading.Thread(target=self.actualizar_estado_luces, daemon=True).start()
        return False
    
    def actualizar_estado_luces(self):
        """Actualiza el estado de las luces"""
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/light"
            response = requests.get(url, headers=self.headers, verify=False)

            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', []):
                    light_id = item.get('id')
                    for device in self.devices.values():
                        if device.get('service_id') == light_id:
                            device['on'] = item.get('on', {}).get('on', False)
                            device['brightness'] = item.get('dimming', {}).get('brightness', 0)

                GLib.idle_add(self.actualizar_interfaz_luces)
                GLib.idle_add(self.actualizar_switches_todas_habitaciones)
        except Exception as e:
            print(f"Error actualizando estado luces: {e}")

    def actualizar_switches_todas_habitaciones(self):
        """Sincroniza el switch de cada habitación con el estado real de sus luces"""
        self._actualizando_switch_habitacion = True
        for room_id, room in self.rooms.items():
            switch = self.switches_habitacion.get(room_id)
            if switch is None:
                continue
            luces_room = [
                self.devices[child['rid']]
                for child in room.get('children', [])
                if child.get('rid') in self.devices
            ]
            alguna_encendida = any(luz.get('on', False) for luz in luces_room)
            print(f"[DEBUG switch] {room.get('name','?'):20s} → luces={[l.get('on') for l in luces_room]}  switch={'ON' if alguna_encendida else 'OFF'}")
            switch.set_active(alguna_encendida)
        self._actualizando_switch_habitacion = False
    
    def actualizar_interfaz_luces(self):
        """Actualiza la interfaz de luces si la habitación actual está seleccionada"""
        if self.habitacion_actual and self.habitacion_actual in self.rooms:
            room = self.rooms.get(self.habitacion_actual)
            if room:
                luces_room = []
                for child in room.get('children', []):
                    if child.get('rid') in self.devices:
                        luces_room.append(self.devices[child.get('rid')])
                self.cargar_luces_habitacion(luces_room)
                
                alguna_encendida = any(luz.get('on', False) for luz in luces_room)
                if self.habitacion_actual in self.switches_habitacion:
                    self._actualizando_switch_habitacion = True
                    self.switches_habitacion[self.habitacion_actual].set_active(alguna_encendida)
                    self._actualizando_switch_habitacion = False
    
    def cargar_luces_habitacion(self, luces):
        """Carga los controles para cada luz"""
        for child in self.contenedor_luces.get_children():
            self.contenedor_luces.remove(child)
        
        self.switches_luces = {}
        self.sliders_luces = {}
        self.botones_color = {}
        
        if not luces:
            label = Gtk.Label()
            label.set_markup("<span foreground='gray'>📭 No hay luces en esta habitación</span>")
            label.set_margin_top(50)
            self.contenedor_luces.pack_start(label, False, False, 0)
        else:
            for luz in luces:
                self.crear_control_luz(luz)
        
        self.contenedor_luces.show_all()
    
    def crear_control_luz(self, luz):
        """Crea un widget de control para una luz individual"""
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        card.get_style_context().add_class("card-luz")
        card.set_margin_bottom(2)
        
        # Botón de color (si la luz soporta color)
        if luz.get('has_color', False):
            btn_color = Gtk.Button(label="🎨")
            btn_color.set_tooltip_text("Seleccionar color")
            btn_color.get_style_context().add_class("btn-color")
            btn_color.set_size_request(50, 40)
            btn_color.connect("clicked", self.on_color_clicked, luz)
            card.pack_start(btn_color, False, False, 0)
            self.botones_color[luz['id']] = btn_color
        
        # Nombre de la luz
        nombre = Gtk.Label()
        nombre_texto = f"<b>{luz['name']}</b>"
        nombre.set_markup(nombre_texto)
        nombre.get_style_context().add_class("nombre-luz")
        nombre.set_halign(Gtk.Align.START)
        nombre.set_size_request(150, -1)
        card.pack_start(nombre, False, False, 0)
        
        # Icono de brillo
        brillo_icono = Gtk.Label()
        brillo_icono.set_markup("💡")
        brillo_icono.set_tooltip_text("Brillo")
        card.pack_start(brillo_icono, False, False, 0)
        
        # Slider de brillo
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_value(luz.get('brightness', 0))
        slider.set_digits(0)
        slider.set_draw_value(False)
        slider.set_hexpand(True)
        slider.set_valign(Gtk.Align.CENTER)
        slider.get_style_context().add_class("compact-slider")
        slider.set_sensitive(luz.get('on', False))
        slider.connect("value-changed", self.on_brillo_changed, luz)
        card.pack_start(slider, True, True, 0)
        
        # Valor del brillo
        valor_brillo = Gtk.Label(label=f"{luz.get('brightness', 0)}%")
        valor_brillo.set_width_chars(4)
        slider.connect("value-changed", self.actualizar_label_brillo, valor_brillo)
        card.pack_start(valor_brillo, False, False, 0)
        
        # Switch de encendido/apagado
        switch = Gtk.Switch()
        switch.set_active(luz.get('on', False))
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("notify::active", self.on_luz_switch_toggled, luz)
        card.pack_start(switch, False, False, 0)
        
        self.contenedor_luces.pack_start(card, False, False, 0)
        
        self.switches_luces[luz['id']] = switch
        self.sliders_luces[luz['id']] = slider
    
    def on_color_clicked(self, widget, luz):
        """Abre el selector de color para la luz"""
        dialog = Gtk.ColorChooserDialog(title=f"Seleccionar color para {luz['name']}", parent=self)
        
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            color = dialog.get_rgba()
            # Convertir Gdk.RGBA a tupla RGB (0-255)
            rgb = (int(color.red * 255), int(color.green * 255), int(color.blue * 255))
            self.cambiar_color(luz, rgb)
        
        dialog.destroy()
    
    def on_luz_switch_toggled(self, switch, gparam, luz):
        """Maneja el cambio del switch de una luz individual"""
        nuevo_estado = switch.get_active()

        # Actualizar la UI inmediatamente (hilo principal)
        switch.handler_block_by_func(self.on_luz_switch_toggled)
        try:
            luz['on'] = nuevo_estado

            if luz['id'] in self.sliders_luces:
                slider = self.sliders_luces[luz['id']]
                slider.handler_block_by_func(self.on_brillo_changed)
                if nuevo_estado:
                    brillo = luz.get('brightness_real', luz.get('brightness', 50))
                    if brillo == 0:
                        brillo = 50
                    slider.set_value(brillo)
                    slider.set_sensitive(True)
                else:
                    brillo_actual = luz.get('brightness', 0)
                    if brillo_actual > 0:
                        luz['brightness_real'] = brillo_actual
                    slider.set_value(0)
                    slider.set_sensitive(False)
                slider.handler_unblock_by_func(self.on_brillo_changed)

            if self.habitacion_actual and self.habitacion_actual in self.rooms:
                room = self.rooms.get(self.habitacion_actual, {})
                luces_room = [
                    self.devices[child.get('rid')]
                    for child in room.get('children', [])
                    if child.get('rid') in self.devices
                ]
                alguna_encendida = any(l.get('on', False) for l in luces_room)
                if self.habitacion_actual in self.switches_habitacion:
                    self._actualizando_switch_habitacion = True
                    self.switches_habitacion[self.habitacion_actual].set_active(alguna_encendida)
                    self._actualizando_switch_habitacion = False
        finally:
            switch.handler_unblock_by_func(self.on_luz_switch_toggled)

        # Enviar comando HTTP en un thread separado para no bloquear la UI
        def enviar_comando():
            try:
                self.controlar_luz(luz, nuevo_estado)
            except Exception as e:
                print(f"Error controlando {luz.get('name')}: {e}")
                GLib.idle_add(self.mostrar_error, f"Error al cambiar estado: {e}")

        threading.Thread(target=enviar_comando, daemon=True).start()
    
    def on_brillo_changed(self, widget, luz):
        """Cambia el brillo de una luz"""
        try:
            porcentaje = int(widget.get_value())
            self.cambiar_brillo(luz, porcentaje)
            luz['brightness'] = porcentaje
            if porcentaje > 0:
                luz['brightness_real'] = porcentaje
            if not luz.get('on'):
                luz['on'] = True
                if luz['id'] in self.switches_luces:
                    luz_switch = self.switches_luces[luz['id']]
                    luz_switch.handler_block_by_func(self.on_luz_switch_toggled)
                    luz_switch.set_active(True)
                    luz_switch.handler_unblock_by_func(self.on_luz_switch_toggled)
        except Exception as e:
            pass
    
    def actualizar_label_brillo(self, widget, label):
        """Actualiza el label del brillo"""
        valor = int(widget.get_value())
        label.set_label(f"{valor}%")
    
    def actualizar_sensores(self):
        """Actualiza los datos de los sensores"""
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/temperature"
            response = requests.get(url, headers=self.headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                updated = False
                
                for item in data.get('data', []):
                    sensor_id = item.get('id')
                    if sensor_id in self.sensors:
                        temperature_data = item.get('temperature', {})
                        temperature_celsius = temperature_data.get('temperature', 0)
                        
                        temperature_report = temperature_data.get('temperature_report', {})
                        if temperature_report:
                            changed_str = temperature_report.get('changed', '')
                            if changed_str:
                                try:
                                    last_changed = datetime.datetime.fromisoformat(changed_str.replace('Z', '+00:00'))
                                    self.sensors[sensor_id]['last_updated'] = last_changed
                                except:
                                    self.sensors[sensor_id]['last_updated'] = datetime.datetime.now()
                        
                        self.sensors[sensor_id]['temperature'] = temperature_celsius
                        updated = True
                
                if updated:
                    GLib.idle_add(self.actualizar_interfaz_sensores)
                    
        except Exception as e:
            print(f"Error actualizando sensores: {e}")
    
    def iniciar_actualizacion_periodica(self):
        """Inicia la actualización periódica de sensores"""
        if self.update_timer is not None:
            try:
                GLib.source_remove(self.update_timer)
            except:
                pass
            self.update_timer = None
        
        if self.bridge_ip and self.api_key:
            self.update_timer = GLib.timeout_add_seconds(self.update_interval, self.actualizar_sensores_periodicamente)
            print(f"Actualización periódica iniciada: cada {self.update_interval // 60} minutos")
        
        return False
    
    def actualizar_sensores_periodicamente(self):
        """Actualiza los sensores periódicamente"""
        if self.bridge_ip and self.api_key:
            threading.Thread(target=self.actualizar_sensores, daemon=True).start()
        return True
    
    def on_dimmers_clicked(self, widget):
        """Abre la ventana de escenas por dimmer"""
        if not self.bridge_ip or not self.headers:
            self.mostrar_error("Conectate al bridge primero")
            return

        dialog = Gtk.Window(title="🔘 Escenas de Dimmers")
        dialog.set_transient_for(self)
        dialog.set_default_size(680, 500)
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        dialog.set_resizable(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)
        vbox.set_margin_start(16)
        vbox.set_margin_end(16)
        dialog.add(vbox)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        titulo = Gtk.Label()
        titulo.set_markup("<span size='large' weight='bold'>🔘 Escenas por Dimmer</span>")
        titulo.set_halign(Gtk.Align.START)
        header.pack_start(titulo, True, True, 0)

        btn_refresh = Gtk.Button(label="🔄 Actualizar")
        btn_refresh.set_halign(Gtk.Align.END)
        header.pack_start(btn_refresh, False, False, 0)
        vbox.pack_start(header, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(sep, False, False, 4)

        spinner = Gtk.Spinner()
        spinner.set_margin_top(40)
        spinner.set_margin_bottom(40)
        spinner.start()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._dim_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._dim_content_box.set_margin_top(6)
        self._dim_content_box.set_margin_bottom(6)
        scroll.add(self._dim_content_box)

        self._dim_stack = Gtk.Stack()
        self._dim_stack.add_named(spinner, "spinner")
        self._dim_stack.add_named(scroll, "contenido")
        self._dim_stack.set_visible_child_name("spinner")
        vbox.pack_start(self._dim_stack, True, True, 0)

        self._dim_resumen = Gtk.Label()
        self._dim_resumen.set_halign(Gtk.Align.START)
        vbox.pack_start(self._dim_resumen, False, False, 4)

        def cargar():
            datos = self.obtener_escenas_dimmers()
            GLib.idle_add(lambda: self.mostrar_escenas_dimmers(datos))

        btn_refresh.connect("clicked", lambda w: threading.Thread(target=cargar, daemon=True).start())

        dialog.show_all()
        threading.Thread(target=cargar, daemon=True).start()

    def obtener_escenas_dimmers(self):
        """Consulta dimmers y sus escenas asociadas via behavior_instance"""
        result = {}
        try:
            url_dev = f"https://{self.bridge_ip}/clip/v2/resource/device"
            resp = requests.get(url_dev, headers=self.headers, verify=False, timeout=8)
            if resp.status_code != 200:
                return {}

            for dev in resp.json().get('data', []):
                services = dev.get('services', [])
                rtypes = [s.get('rtype') for s in services]
                if 'button' in rtypes:
                    device_id = dev['id']
                    button_rids = [s['rid'] for s in services if s.get('rtype') == 'button']
                    result[device_id] = {
                        'name': dev.get('metadata', {}).get('name', 'Dimmer'),
                        'button_rids': button_rids,
                        'scenes': [],
                        'bi_id': None,
                        'btn_rid_with_slots': None,
                        'full_config': None,
                        'available_scenes': [],
                    }

            if not result:
                return {}

            url_bi = f"https://{self.bridge_ip}/clip/v2/resource/behavior_instance"
            resp_bi = requests.get(url_bi, headers=self.headers, verify=False, timeout=8)

            if resp_bi.status_code == 200:
                for bi in resp_bi.json().get('data', []):
                    config = bi.get('configuration', {})
                    config_str = json.dumps(config)

                    matched_id = None
                    for dev_id, dimmer in result.items():
                        if dev_id in config_str:
                            matched_id = dev_id
                            break
                        for btn_rid in dimmer['button_rids']:
                            if btn_rid in config_str:
                                matched_id = dev_id
                                break
                        if matched_id:
                            break

                    if not matched_id:
                        continue

                    result[matched_id]['bi_id'] = bi['id']
                    result[matched_id]['full_config'] = config

                    for btn_rid_key, btn_data in config.get('buttons', {}).items():
                        slots = (btn_data
                                 .get('on_short_release', {})
                                 .get('scene_cycle_extended', {})
                                 .get('slots', []))
                        if not slots:
                            continue

                        result[matched_id]['btn_rid_with_slots'] = btn_rid_key

                        # Detectar room_id para saber qué escenas ofrecer
                        where = btn_data.get('where', [{}])
                        room_id = where[0].get('group', {}).get('rid', '') if where else ''

                        # Escenas disponibles en esa habitación
                        available = sorted(
                            [{'id': sid, 'name': s['name'], 'icon': s.get('icon', '🎨')}
                             for sid, s in self.scenes.items()
                             if s.get('group_rid') == room_id],
                            key=lambda s: s['name']
                        )
                        result[matched_id]['available_scenes'] = available

                        for slot in slots:
                            for action_entry in slot:
                                scene_rid = (action_entry
                                             .get('action', {})
                                             .get('recall', {})
                                             .get('rid', ''))
                                if scene_rid and scene_rid in self.scenes:
                                    scene = self.scenes[scene_rid]
                                    if not any(s['id'] == scene_rid
                                               for s in result[matched_id]['scenes']):
                                        result[matched_id]['scenes'].append({
                                            'id': scene_rid,
                                            'name': scene['name'],
                                            'icon': scene.get('icon', '🎨'),
                                        })

        except Exception as e:
            print(f"Error obteniendo escenas de dimmers: {e}")
            import traceback
            traceback.print_exc()

        return result

    def mostrar_escenas_dimmers(self, datos):
        """Rellena el diálogo de dimmers con los resultados"""
        for child in self._dim_content_box.get_children():
            self._dim_content_box.remove(child)

        total_dimmers = len(datos)
        total_escenas = sum(len(d['scenes']) for d in datos.values())

        if not datos:
            lbl = Gtk.Label()
            lbl.set_markup("<span foreground='gray'>No se encontraron dimmers / switches</span>")
            lbl.set_margin_top(40)
            self._dim_content_box.pack_start(lbl, False, False, 0)
        else:
            for dev_id, dimmer in sorted(datos.items(), key=lambda x: x[1]['name']):
                frame = Gtk.Frame()
                frame.set_margin_start(4)
                frame.set_margin_end(4)

                inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                inner.set_margin_top(10)
                inner.set_margin_bottom(10)
                inner.set_margin_start(12)
                inner.set_margin_end(12)
                frame.add(inner)

                lbl_nombre = Gtk.Label()
                lbl_nombre.set_markup(f"<b>🔘 {GLib.markup_escape_text(dimmer['name'])}</b>")
                lbl_nombre.set_halign(Gtk.Align.START)
                inner.pack_start(lbl_nombre, False, False, 0)

                if dimmer['scenes'] and dimmer['bi_id']:
                    available = dimmer['available_scenes']
                    available_ids = [s['id'] for s in available]

                    # Una ComboBox por pulsación
                    combos = []
                    for pos, sc in enumerate(dimmer['scenes'], start=1):
                        fila = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                        fila.set_margin_top(2)

                        lbl_btn = Gtk.Label()
                        lbl_btn.set_markup(f"<span foreground='gray'>Pulsación {pos}:</span>")
                        lbl_btn.set_halign(Gtk.Align.START)
                        lbl_btn.set_width_chars(12)
                        fila.pack_start(lbl_btn, False, False, 0)

                        combo = Gtk.ComboBoxText()
                        combo.connect("scroll-event", lambda w, e: True)
                        for av_sc in available:
                            combo.append_text(f"{av_sc['icon']} {av_sc['name']}")

                        # Seleccionar la escena actual
                        if sc['id'] in available_ids:
                            combo.set_active(available_ids.index(sc['id']))
                        else:
                            combo.set_active(0)

                        fila.pack_start(combo, True, True, 0)
                        inner.pack_start(fila, False, False, 0)
                        combos.append((combo, available_ids))

                    # Botón Guardar
                    btn_guardar = Gtk.Button(label="💾 Guardar")
                    btn_guardar.set_halign(Gtk.Align.END)
                    btn_guardar.set_margin_top(6)
                    btn_guardar.connect(
                        "clicked",
                        self.guardar_escenas_dimmer,
                        dimmer, combos
                    )
                    inner.pack_start(btn_guardar, False, False, 0)

                else:
                    lbl_ninguna = Gtk.Label()
                    lbl_ninguna.set_markup("<span foreground='gray' size='small'>Sin escenas asociadas en behavior_instance</span>")
                    lbl_ninguna.set_halign(Gtk.Align.START)
                    inner.pack_start(lbl_ninguna, False, False, 0)

                self._dim_content_box.pack_start(frame, False, False, 0)

        self._dim_resumen.set_markup(
            f"<b>{total_dimmers}</b> dimmers · <b>{total_escenas}</b> escenas encontradas"
        )
        self._dim_stack.set_visible_child_name("contenido")
        self._dim_content_box.show_all()

    def guardar_escenas_dimmer(self, widget, dimmer, combos):
        """Guarda los cambios de escenas en el behavior_instance via PUT"""
        widget.set_sensitive(False)
        widget.set_label("⏳ Guardando...")

        # Recoger IDs seleccionados en el orden de las ComboBox
        new_scene_rids = []
        for combo, available_ids in combos:
            idx = combo.get_active()
            if idx >= 0 and idx < len(available_ids):
                new_scene_rids.append(available_ids[idx])

        def _enviar():
            try:
                config = dimmer['full_config']
                btn_rid = dimmer['btn_rid_with_slots']

                # Reconstruir slots con los nuevos scene RIDs
                new_slots = [
                    [{"action": {"recall": {"rid": rid, "rtype": "scene"}}}]
                    for rid in new_scene_rids
                ]
                config['buttons'][btn_rid]['on_short_release']['scene_cycle_extended']['slots'] = new_slots

                url = f"https://{self.bridge_ip}/clip/v2/resource/behavior_instance/{dimmer['bi_id']}"
                resp = requests.put(
                    url,
                    headers=self.headers,
                    json={"configuration": config},
                    verify=False,
                    timeout=8
                )

                if resp.status_code in (200, 204):
                    # Actualizar escenas en memoria con los nuevos valores
                    dimmer['scenes'] = [
                        {
                            'id': rid,
                            'name': self.scenes[rid]['name'],
                            'icon': self.scenes[rid].get('icon', '🎨'),
                        }
                        for rid in new_scene_rids
                        if rid in self.scenes
                    ]
                    GLib.idle_add(lambda: widget.set_label("✅ Guardado"))
                else:
                    print(f"Error PUT behavior_instance: {resp.status_code} {resp.text}")
                    GLib.idle_add(lambda: widget.set_label("❌ Error"))
            except Exception as e:
                print(f"Error guardando escenas dimmer: {e}")
                GLib.idle_add(lambda: widget.set_label("❌ Error"))
            finally:
                GLib.idle_add(lambda: widget.set_sensitive(True))

        threading.Thread(target=_enviar, daemon=True).start()

    # ─── Música / Entertainment API ────────────────────────────────────────────

    def on_musica_clicked(self, widget):
        if not self.bridge_ip or not self.headers:
            self.mostrar_error("Conectate al bridge primero")
            return
        if not self.config.get('ent_clientkey'):
            self._mostrar_dialogo_registro()
        else:
            self._mostrar_ventana_musica()

    def _mostrar_dialogo_registro(self):
        dialog = Gtk.Dialog(title="Registrar Entertainment API", transient_for=self,
                            modal=True)
        dialog.set_default_size(420, 220)
        content = dialog.get_content_area()
        content.set_spacing(8)

        lbl = Gtk.Label()
        lbl.set_markup(
            "<b>Para sincronizar con música necesitás registrar la app.\n\n"
            "1. Presioná el botón físico del bridge Hue.\n"
            "2. Hacé click en <i>Registrar</i> dentro de 30 segundos.</b>"
        )
        lbl.set_margin_top(16)
        lbl.set_margin_start(16)
        lbl.set_margin_end(16)
        lbl.set_line_wrap(True)
        content.pack_start(lbl, False, False, 0)

        status_lbl = Gtk.Label(label="")
        status_lbl.set_margin_start(16)
        content.pack_start(status_lbl, False, False, 0)

        btn_reg = Gtk.Button(label="🔗 Registrar")
        btn_reg.set_margin_start(16)
        btn_reg.set_margin_end(16)
        btn_reg.set_margin_bottom(12)
        content.pack_start(btn_reg, False, False, 0)

        dialog.show_all()

        def _hacer_registro(w):
            w.set_sensitive(False)
            w.set_label("⏳ Registrando...")

            def _reg():
                try:
                    url = f"https://{self.bridge_ip}/api"
                    resp = requests.post(
                        url,
                        json={"devicetype": "hue_sync_linux", "generateclientkey": True},
                        verify=False, timeout=12,
                    )
                    data = resp.json()
                    if isinstance(data, list) and 'success' in data[0]:
                        uname = data[0]['success']['username']
                        ckey  = data[0]['success']['clientkey']
                        self.config['ent_username'] = uname
                        self.config['ent_clientkey'] = ckey
                        self.guardar_configuracion()
                        GLib.idle_add(lambda: [
                            status_lbl.set_markup("<span foreground='green'>✅ Registrado correctamente</span>"),
                            w.set_label("✅ Listo"),
                        ] and dialog.response(Gtk.ResponseType.OK))
                    else:
                        err = (data[0].get('error', {}).get('description', str(data))
                               if isinstance(data, list) else str(data))
                        GLib.idle_add(lambda err=err: [
                            status_lbl.set_markup(f"<span foreground='red'>❌ {err}</span>"),
                            w.set_sensitive(True),
                            w.set_label("🔗 Reintentar"),
                        ])
                except Exception as e:
                    GLib.idle_add(lambda e=e: [
                        status_lbl.set_markup(f"<span foreground='red'>❌ {e}</span>"),
                        w.set_sensitive(True),
                        w.set_label("🔗 Reintentar"),
                    ])

            threading.Thread(target=_reg, daemon=True).start()

        btn_reg.connect("clicked", _hacer_registro)
        resp = dialog.run()
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            GLib.idle_add(self._mostrar_ventana_musica)

    def _obtener_entertainment_areas(self):
        try:
            url = f"https://{self.bridge_ip}/clip/v2/resource/entertainment_configuration"
            resp = requests.get(url, headers=self.headers, verify=False, timeout=6)
            return [
                {
                    'id': a['id'],
                    'name': a['name'],
                    'channels': a['channels'],
                    'id_v1': a.get('id_v1', '').split('/')[-1],  # "200"
                }
                for a in resp.json().get('data', [])
            ]
        except Exception as e:
            print(f"[ENTERTAINMENT] Error obteniendo áreas: {e}")
            return []

    def _mostrar_ventana_musica(self):
        if hasattr(self, '_win_musica') and self._win_musica:
            self._win_musica.present()
            return

        win = Gtk.Window(title="🎵 Sync Música — Hue")
        win.set_default_size(460, 310)
        win.set_transient_for(self)
        self._win_musica = win
        self._sync_manager = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(18)
        vbox.set_margin_bottom(18)
        vbox.set_margin_start(22)
        vbox.set_margin_end(22)
        win.add(vbox)

        def _fila(lbl_txt, widget):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl = Gtk.Label(label=lbl_txt)
            lbl.set_width_chars(18)
            lbl.set_halign(Gtk.Align.START)
            row.pack_start(lbl, False, False, 0)
            row.pack_start(widget, True, True, 0)
            vbox.pack_start(row, False, False, 0)

        # Área de Entertainment
        areas = self._obtener_entertainment_areas()
        combo_area = Gtk.ComboBoxText()
        combo_area.connect("scroll-event", lambda w, e: True)
        for a in areas:
            combo_area.append_text(a['name'])
        if areas:
            combo_area.set_active(0)
        _fila("Área Entertainment:", combo_area)

        # Efecto
        EFECTOS = [('pulse', '🎵 Pulso de color'), ('spectrum', '🌈 Espectro L/C/R'), ('fire', '🔥 Fuego'), ('coral', '🎤 Coral (voz)')]
        combo_efecto = Gtk.ComboBoxText()
        combo_efecto.connect("scroll-event", lambda w, e: True)
        for _, nombre in EFECTOS:
            combo_efecto.append_text(nombre)
        combo_efecto.set_active(0)
        _fila("Efecto:", combo_efecto)

        # Fuente de audio (fuentes PulseAudio/PipeWire)
        fuentes = self._obtener_fuentes_audio()
        combo_dev = Gtk.ComboBoxText()
        combo_dev.connect("scroll-event", lambda w, e: True)
        default_pos = 0
        for pos, (src_id, label) in enumerate(fuentes):
            combo_dev.append_text(label)
            if 'monitor' in src_id.lower() or 'monitor' in label.lower():
                default_pos = pos
        combo_dev.set_active(default_pos)

        fila_audio = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_audio = Gtk.Label(label="Fuente de audio:")
        lbl_audio.set_width_chars(18)
        lbl_audio.set_halign(Gtk.Align.START)
        fila_audio.pack_start(lbl_audio, False, False, 0)
        fila_audio.pack_start(combo_dev, True, True, 0)

        btn_app = Gtk.Button(label="🎵")
        btn_app.set_tooltip_text("Capturar audio de una aplicación específica")
        btn_app.connect("clicked", lambda _: self._mostrar_selector_app(combo_dev, fuentes, status_lbl))
        fila_audio.pack_start(btn_app, False, False, 0)
        vbox.pack_start(fila_audio, False, False, 0)

        # Estado
        status_lbl = Gtk.Label(label="Listo para conectar")
        status_lbl.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(status_lbl, False, False, 4)

        # Botón Start/Stop
        btn = Gtk.Button(label="▶  Iniciar Sync")
        btn.set_size_request(-1, 42)
        vbox.pack_start(btn, False, False, 0)

        def _detener_sync_timer():
            if getattr(self, '_sync_refresh_timer', None):
                GLib.source_remove(self._sync_refresh_timer)
                self._sync_refresh_timer = None

        def _tick_refresh_sync():
            if self._sync_manager:
                threading.Thread(target=self.actualizar_estado_luces, daemon=True).start()
                return True  # seguir repitiendo
            self._sync_refresh_timer = None
            return False  # detener timer

        def _toggle(w):
            if self._sync_manager:
                _detener_sync_timer()
                try:
                    self._sync_manager.detener()
                except Exception as ex:
                    print(f"[TOGGLE] Error al detener: {ex}")
                self._sync_manager = None
                w.set_label("▶  Iniciar Sync")
                status_lbl.set_text("Detenido")
                combo_area.set_sensitive(True)
                combo_efecto.set_sensitive(True)
                combo_dev.set_sensitive(True)
                threading.Thread(target=self.actualizar_estado_luces, daemon=True).start()
                return

            if not areas:
                status_lbl.set_markup("<span foreground='red'>❌ No hay áreas configuradas en la app Hue</span>")
                return

            w.set_sensitive(False)
            combo_area.set_sensitive(False)
            combo_efecto.set_sensitive(False)
            combo_dev.set_sensitive(False)
            status_lbl.set_text("⏳ Conectando via DTLS…")

            area       = areas[combo_area.get_active()]
            efecto     = EFECTOS[combo_efecto.get_active()][0]
            source_id  = fuentes[combo_dev.get_active()][0] if fuentes else None

            def _iniciar():
                try:
                    mgr = HueSyncManager(
                        self.bridge_ip,
                        self.config['ent_username'],
                        self.config['ent_clientkey'],
                        self.headers,
                    )
                    mgr.conectar(area['id'], area['channels'], efecto, area['id_v1'])
                    mgr.iniciar_audio(source_name=source_id)
                    self._sync_manager = mgr
                    # Arrancar timer de refresh desde el hilo principal (thread-safe)
                    GLib.idle_add(lambda: (
                        setattr(self, '_sync_refresh_timer',
                                GLib.timeout_add_seconds(3, _tick_refresh_sync))
                        or False
                    ))
                    GLib.idle_add(lambda: [
                        status_lbl.set_markup("<span foreground='#2ecc71'><b>🎵 Sincronizando…</b></span>"),
                        w.set_label("⏹  Detener"),
                        w.set_sensitive(True),
                    ])
                except Exception as e:
                    GLib.idle_add(lambda e=e: [
                        status_lbl.set_markup(f"<span foreground='red'>❌ {e}</span>"),
                        w.set_sensitive(True),
                        combo_area.set_sensitive(True),
                        combo_efecto.set_sensitive(True),
                        combo_dev.set_sensitive(True),
                    ])

            threading.Thread(target=_iniciar, daemon=True).start()

        btn.connect("clicked", _toggle)

        def _on_close(w, event):
            _detener_sync_timer()
            if self._sync_manager:
                self._sync_manager.detener()
                self._sync_manager = None
            self._restaurar_audio_firefox()
            self._win_musica = None
            threading.Thread(target=self.actualizar_estado_luces, daemon=True).start()
            return False

        win.connect("delete-event", _on_close)
        win.show_all()

    def _obtener_fuentes_audio(self):
        """Lista fuentes de PulseAudio/PipeWire disponibles."""
        import subprocess as _sp
        fuentes = []
        try:
            out = _sp.run(['pactl', 'list', 'sources', 'short'],
                          capture_output=True, text=True, timeout=3).stdout
            for line in out.strip().splitlines():
                parts = [p for p in line.split('\t') if p.strip()]
                if len(parts) < 2:
                    continue
                name = parts[1].strip()
                if not name:
                    continue
                if name.endswith('.monitor'):
                    base = name.replace('.monitor', '')
                    short = base.split('.')[-2] if '.' in base else base
                    label = f"🔊 {short} (monitor)"
                elif 'input' in name.lower() or 'analog' in name.lower():
                    label = f"🎤 {name.split('.')[-1]}"
                else:
                    label = f"📡 {name}"
                fuentes.append((name, label))
        except Exception as e:
            print(f"[AUDIO] Error listando fuentes: {e}")
        return fuentes

    def _obtener_sink_inputs_activos(self):
        """Retorna lista de (sink_input_id, app_name, current_sink) para todas las apps con audio."""
        import subprocess as _sp, re as _re
        try:
            si_out = _sp.run(['pactl', 'list', 'sink-inputs'],
                              capture_output=True, text=True, timeout=3).stdout
        except Exception:
            return []
        apps, current_id, current_sink, current_name = [], None, None, None
        for line in si_out.splitlines():
            m = _re.match(r'.*#(\d+)', line.strip())
            if m and line.strip()[0].isupper():
                if current_id and current_name:
                    apps.append((current_id, current_name, current_sink))
                current_id, current_sink, current_name = m.group(1), None, None
            sm = _re.match(r'\s+Sink:\s+(\S+)', line)
            if sm and current_id:
                current_sink = sm.group(1)
            nm = _re.search(r'application\.name\s*=\s*"([^"]+)"', line)
            if nm and current_id and not current_name:
                current_name = nm.group(1)
            bm = _re.search(r'application\.process\.binary\s*=\s*"([^"]+)"', line)
            if bm and current_id and not current_name:
                current_name = bm.group(1)
        if current_id and current_name:
            apps.append((current_id, current_name, current_sink))
        return apps

    def _mostrar_selector_app(self, combo_dev, fuentes, status_lbl):
        """Muestra un diálogo para elegir qué app capturar."""
        apps = self._obtener_sink_inputs_activos()
        if not apps:
            status_lbl.set_markup(
                "<span foreground='orange'>⚠ No hay aplicaciones con audio activo</span>")
            return

        dialog = Gtk.Dialog(title="Capturar audio de aplicación",
                            transient_for=self)
        dialog.set_default_size(340, 280)
        area = dialog.get_content_area()
        area.set_spacing(8)
        area.set_margin_top(12)
        area.set_margin_bottom(8)
        area.set_margin_start(14)
        area.set_margin_end(14)

        area.add(Gtk.Label(label="Seleccioná la aplicación a sincronizar con las luces:"))

        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(140)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        # Agrupar sink-inputs por nombre de app
        from collections import defaultdict as _dd
        grupos = _dd(list)
        for sid, name, sink in apps:
            grupos[name].append((sid, sink))
        for name, inputs in grupos.items():
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label=name)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_margin_start(10)
            lbl.set_margin_top(6)
            lbl.set_margin_bottom(6)
            row.add(lbl)
            row._app_name = name
            row._app_inputs = inputs  # [(sid, orig_sink), ...]
            listbox.add(row)

        listbox.select_row(listbox.get_row_at_index(0))
        scroll.add(listbox)
        area.add(scroll)
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        dialog.add_button("Capturar", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()

        response = dialog.run()
        selected = listbox.get_selected_row()
        dialog.destroy()

        if response == Gtk.ResponseType.OK and selected:
            self._configurar_sink_app(
                selected._app_inputs, selected._app_name, combo_dev, fuentes, status_lbl)

    def _configurar_sink_app(self, inputs, app_name, combo_dev, fuentes, status_lbl):
        """Crea sink virtual + loopback y mueve los sink-inputs de la app seleccionada."""
        import subprocess as _sp
        SINK = 'hue_app_sink'

        def _hacer():
            try:
                # Crear null sink si no existe
                sinks = _sp.run(['pactl', 'list', 'sinks', 'short'],
                                capture_output=True, text=True, timeout=3).stdout
                if SINK not in sinks:
                    r = _sp.run(['pactl', 'load-module', 'module-null-sink',
                                 f'sink_name={SINK}',
                                 f'sink_properties=device.description=HueAppSync'],
                                capture_output=True, text=True, check=True, timeout=5)
                    self._hue_sink_module = r.stdout.strip()

                    # Loopback: sink virtual → salida real (parlante/Bluetooth)
                    default_sink = _sp.run(['pactl', 'get-default-sink'],
                                           capture_output=True, text=True, timeout=3).stdout.strip()
                    if default_sink and default_sink != SINK:
                        lb = _sp.run(['pactl', 'load-module', 'module-loopback',
                                      f'source={SINK}.monitor',
                                      f'sink={default_sink}',
                                      'latency_msec=100'],
                                     capture_output=True, text=True, timeout=5)
                        self._hue_loopback_module = lb.stdout.strip()

                # Guardar originales y mover al sink virtual
                if not hasattr(self, '_firefox_originals'):
                    self._firefox_originals = {}
                for fid, orig_sink in inputs:
                    if orig_sink:
                        self._firefox_originals[fid] = orig_sink
                    _sp.run(['pactl', 'move-sink-input', fid, SINK],
                            check=True, timeout=5)

                monitor = f'{SINK}.monitor'
                GLib.idle_add(lambda: _actualizar_combo(monitor))

            except Exception as e:
                GLib.idle_add(lambda e=e: status_lbl.set_markup(
                    f"<span foreground='red'>❌ {e}</span>"))

        def _actualizar_combo(monitor):
            label = f'🎵 {app_name} (captura)'
            for i, (src_id, _) in enumerate(fuentes):
                if src_id == monitor:
                    combo_dev.set_active(i)
                    status_lbl.set_markup(
                        f"<span foreground='#2ecc71'>🎵 {app_name} enrutado al sink virtual</span>")
                    return
            fuentes.append((monitor, label))
            combo_dev.append_text(label)
            combo_dev.set_active(len(fuentes) - 1)
            status_lbl.set_markup(
                f"<span foreground='#2ecc71'>🎵 {app_name} enrutado al sink virtual</span>")

        status_lbl.set_text(f"⏳ Configurando captura de {app_name}…")
        threading.Thread(target=_hacer, daemon=True).start()

    def _restaurar_audio_firefox(self):
        """Restaura los sink-inputs al sink original y descarga el sink virtual."""
        import subprocess as _sp
        originals = getattr(self, '_firefox_originals', {})
        for fid, orig_sink in originals.items():
            try:
                _sp.run(['pactl', 'move-sink-input', fid, orig_sink],
                        timeout=3, capture_output=True)
            except Exception:
                pass
        self._firefox_originals = {}
        hubo_modulos = False
        for attr in ('_hue_loopback_module', '_hue_sink_module'):
            mod = getattr(self, attr, None)
            if mod:
                hubo_modulos = True
                try:
                    _sp.run(['pactl', 'unload-module', mod],
                            timeout=3, capture_output=True)
                except Exception:
                    pass
                setattr(self, attr, None)
        if hubo_modulos:
            # Limpiar entradas de nuestros sinks del archivo de estado de WirePlumber
            # sin reiniciarlo (reiniciarlo desconecta el Bluetooth)
            self._limpiar_wp_restore_stream()

    def _limpiar_wp_restore_stream(self):
        import os as _os
        wp_path = _os.path.expanduser('~/.local/state/wireplumber/restore-stream')
        if not _os.path.exists(wp_path):
            return
        try:
            with open(wp_path, 'r') as f:
                lines = f.readlines()
            clean = [l for l in lines
                     if 'hue_app_sink' not in l and 'hue_firefox_sink' not in l]
            if len(clean) != len(lines):
                with open(wp_path, 'w') as f:
                    f.writelines(clean)
        except Exception:
            pass

    def mostrar_error(self, mensaje):
        """Muestra un diálogo de error"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(mensaje)
        dialog.run()
        dialog.destroy()

class HueSyncManager:
    """Maneja la conexión DTLS con la Hue Entertainment API y el análisis de audio."""

    SAMPLERATE = 44100
    BLOCKSIZE = 1024

    def __init__(self, bridge_ip, username, clientkey, headers):
        self.bridge_ip = bridge_ip
        self.username = username
        self.clientkey = clientkey
        self.headers = headers
        self._sock = None
        self._stream = None
        self._running = False
        self._seq = 0
        self._channels = []
        self._effect = 'pulse'
        self._cola = queue.Queue(maxsize=4)
        self._area_id = None
        self._group_id_v1 = None
        self._peak = 0.01
        self._hue = 0.0
        self._coral_base_rgb = {}

    def conectar(self, area_id, channels, effect='pulse', group_id_v1=None):
        self._area_id = area_id
        self._group_id_v1 = group_id_v1
        self._effect = effect

        import requests as _req

        # Resolver canal → light_v1_id usando la API v2
        ent_resp = _req.get(f'https://{self.bridge_ip}/clip/v2/resource/entertainment',
            headers=self.headers, verify=False, timeout=6)
        ent_map = {}  # entertainment_rid → light_rid
        for e in ent_resp.json().get('data', []):
            rr = e.get('renderer_reference')
            if rr and rr.get('rtype') == 'light':
                ent_map[e['id']] = rr['rid']

        lights_resp = _req.get(f'https://{self.bridge_ip}/clip/v2/resource/light',
            headers=self.headers, verify=False, timeout=6)
        light_v1_map = {}   # light_rid → v1 integer id
        light_v1_xy  = {}   # v1 integer id → (x, y, bri_pct)
        for l in lights_resp.json().get('data', []):
            id_v1 = l.get('id_v1', '')
            if id_v1.startswith('/lights/'):
                v1 = int(id_v1.split('/')[-1])
                light_v1_map[l['id']] = v1
                xy  = l.get('color', {}).get('xy', {})
                bri = l.get('dimming', {}).get('brightness', 100)
                light_v1_xy[v1] = (xy.get('x', 0.5), xy.get('y', 0.4), bri)

        self._channels = []
        for ch in channels:
            pos = ch.get('position', {})
            for member in ch.get('members', []):
                ent_rid = member['service']['rid']
                light_rid = ent_map.get(ent_rid)
                v1_id = light_v1_map.get(light_rid) if light_rid else None
                if v1_id is not None:
                    self._channels.append({'light_v1_id': v1_id, 'position': pos})

        if effect == 'coral':
            self._coral_base_rgb = {}
            for ch in self._channels:
                v1_id = ch['light_v1_id']
                xy_bri = light_v1_xy.get(v1_id, (0.5, 0.4, 100))
                self._coral_base_rgb[v1_id] = self._xy_bri_to_rgb(*xy_bri)

        # Activar streaming via API v1
        resp = _req.put(
            f'https://{self.bridge_ip}/api/{self.username}/groups/{group_id_v1}',
            json={'stream': {'active': True}}, verify=False, timeout=6
        )
        result = resp.json()
        if isinstance(result, list) and result and result[0].get('error'):
            raise RuntimeError(f"Error activando stream v1: {result[0]['error']}")

        from mbedtls import tls as _tls
        import socket as _socket
        conf = _tls.DTLSConfiguration(
            validate_certificates=False,
            ciphers=['TLS-PSK-WITH-AES-128-GCM-SHA256'],
            lowest_supported_version=_tls.DTLSVersion.DTLSv1_2,
            highest_supported_version=_tls.DTLSVersion.DTLSv1_2,
            pre_shared_key=(self.username, bytes.fromhex(self.clientkey)),
        )
        ctx = _tls.ClientContext(conf)
        rawsock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        rawsock.settimeout(8.0)
        self._sock = ctx.wrap_socket(rawsock, server_hostname=self.bridge_ip)
        self._sock.connect((self.bridge_ip, 2100))
        self._sock.do_handshake()

    def iniciar_audio(self, source_name=None, device_idx=None):
        self._running = True
        self._sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self._sender_thread.start()

        import sounddevice as sd
        if source_name:
            os.environ['PULSE_SOURCE'] = source_name
            device = 'pulse'
        else:
            device = device_idx

        self._stream = sd.InputStream(
            samplerate=self.SAMPLERATE,
            blocksize=self.BLOCKSIZE,
            channels=2,
            dtype='float32',
            device=device,
            callback=self._audio_callback,
        )
        self._stream.start()

    def _audio_callback(self, indata, frames, time_info, status):
        import numpy as np
        rms = float(np.sqrt(np.mean(indata ** 2)))

        # Silencio: apagar luces
        if rms < 0.001:
            try:
                self._cola.put_nowait((0.0, 0.0, 0.0, 0.0, 0.0))
            except queue.Full:
                pass
            return

        # Brillo: rms vs pico reciente (adaptive gain)
        self._peak = max(self._peak * 0.995, rms)
        brightness = min(1.0, rms / self._peak)

        # FFT
        mono  = indata[:, 0] * np.hanning(len(indata[:, 0]))
        fft   = np.abs(np.fft.rfft(mono))
        freqs = np.fft.rfftfreq(len(mono), 1.0 / self.SAMPLERATE)

        def _band(lo, hi):
            m = (freqs >= lo) & (freqs < hi)
            return float(np.mean(fft[m])) if m.any() else 0.0

        bass   = _band(20, 250)
        mid    = _band(250, 2000)
        treble = _band(2000, 16000)
        vocal  = _band(200, 2500)

        # Normalizar bandas entre sí: color = proporción relativa
        total = bass + mid + treble + 1e-9
        bass_n   = bass   / total
        mid_n    = mid    / total
        treble_n = treble / total
        vocal_n  = vocal  / total  # fracción de energía en rango vocal

        try:
            self._cola.put_nowait((brightness, bass_n, mid_n, treble_n, vocal_n))
        except queue.Full:
            pass

    def _sender_loop(self):
        while self._running:
            try:
                datos = self._cola.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                rgb_list = self._calcular_colores(*datos)
                self._enviar(rgb_list)
            except Exception as e:
                print(f"[SYNC] Error: {e}")
                self._running = False
                break

    @staticmethod
    def _xy_bri_to_rgb(x, y, bri_pct):
        if y == 0:
            return (255, 255, 255)
        Y = bri_pct / 100.0
        X = (Y / y) * x
        Z = (Y / y) * (1.0 - x - y)
        r =  X * 1.656492 - Y * 0.354851 - Z * 0.255038
        g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152
        b =  X * 0.051713 - Y * 0.121364 + Z * 1.011530
        def _gamma(v):
            return max(0.0, v) ** (1.0 / 2.2)
        r, g, b = _gamma(r), _gamma(g), _gamma(b)
        mx = max(r, g, b, 1.0)
        return (int(r / mx * 255), int(g / mx * 255), int(b / mx * 255))

    def _calcular_colores(self, brightness, bass, mid, treble, vocal=0.5):
        import colorsys as _cs
        brightness = min(1.0, brightness)
        result = []
        if self._effect == 'pulse':
            # Hue cycling: avanza más rápido en momentos de mayor energía
            self._hue = (self._hue + 0.3 + brightness * 1.5) % 360
            rf, gf, bf = _cs.hsv_to_rgb(self._hue / 360.0, 1.0, brightness)
            r, g, b = int(rf * 255), int(gf * 255), int(bf * 255)
            for ch in self._channels:
                result.append((ch['light_v1_id'], r, g, b))
        elif self._effect == 'spectrum':
            for ch in self._channels:
                x        = ch.get('position', {}).get('x', 0.0)
                w_bass   = max(0.0, -x)
                w_treble = max(0.0,  x)
                w_mid    = 1.0 - abs(x)
                r = int(bass   * w_bass   * brightness * 255)
                g = int(mid    * w_mid    * brightness * 255)
                b = int(treble * w_treble * brightness * 255)
                result.append((ch['light_v1_id'], r, g, b))
        elif self._effect == 'fire':
            r = min(255, int(brightness * 255))
            g = min(255, int(brightness * bass * 180))
            for ch in self._channels:
                result.append((ch['light_v1_id'], r, g, 0))
        elif self._effect == 'coral':
            # Escala el color actual de cada luz según la energía vocal (200-2500 Hz)
            # vocal ya viene normalizado; mezclamos con brightness general
            effective = brightness * (0.25 + 0.75 * vocal)
            effective = min(1.0, effective)
            for ch in self._channels:
                br, bg, bb = self._coral_base_rgb.get(ch['light_v1_id'], (255, 220, 180))
                result.append((ch['light_v1_id'],
                                int(br * effective),
                                int(bg * effective),
                                int(bb * effective)))
        return result

    def _enviar(self, channels_rgb):
        hdr = b'HueStream' + bytes([0x01, 0x00, self._seq & 0xFF, 0x00, 0x00, 0x00, 0x00])
        self._seq += 1
        data = b''
        for lid, r, g, b in channels_rgb:
            data += bytes([0x00, (lid >> 8) & 0xFF, lid & 0xFF])
            data += struct.pack('!HHH', min(65535, r * 257), min(65535, g * 257), min(65535, b * 257))
        self._sock.send(hdr + data)

    def detener(self):
        self._running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        if self._group_id_v1:
            try:
                import requests as _req
                _req.put(
                    f'https://{self.bridge_ip}/api/{self.username}/groups/{self._group_id_v1}',
                    json={'stream': {'active': False}}, verify=False, timeout=4
                )
            except Exception:
                pass


def main():
    app = AppHueMejorada()
    def _on_app_destroy(w):
        w._restaurar_audio_firefox()
        Gtk.main_quit()
    app.connect("destroy", _on_app_destroy)
    Gtk.main()

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
