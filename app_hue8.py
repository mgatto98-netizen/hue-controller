#!/usr/bin/env python3
# app_hue_mejorada.py
# Aplicación para controlar luces Philips Hue en Linux

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
from phue import Bridge
import threading
import sys
import os
import json

class AppHueMejorada(Gtk.Window):
    def __init__(self):
        super().__init__(title="Philips Hue Controller - Control de Luces por Habitaciones")
        
        # Configuración de la ventana
        self.set_default_size(1080, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Variables
        self.bridge = None
        self.grupos = {}  # Diccionario para almacenar los grupos y sus luces
        self.luces = {}   # Diccionario para almacenar todas las luces
        self.luces_sin_grupo = []  # Luces que no están en ningún grupo
        self.escenas_por_grupo = {}  # Diccionario para almacenar escenas por grupo
        self.luces_info = {}  # Información adicional de las luces (si soportan color)
        
        # Archivo de configuración para guardar la IP
        self.config_file = os.path.expanduser("~/.hue_controller_config.json")
        self.config = self.cargar_configuracion()
        
        # Estilo CSS
        self.aplicar_estilos()
        
        # Crear la interfaz
        self.crear_interfaz()
        
        self.show_all()
    
    def cargar_configuracion(self):
        """Carga la configuración guardada"""
        config_default = {
            "bridge_ip": "192.168.68.54"  # IP por defecto configurada
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
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
        css = b"""
        * {
            font-family: 'Segoe UI', 'Ubuntu', 'Cantarell', sans-serif;
        }
        
        .sidebar {
            background-color: #2c3e50;
            padding: 10px;
        }
        
        .sidebar button {
            background-color: #34495e;
            color: white;
            border: none;
            padding: 12px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .sidebar button:hover {
            background-color: #3498db;
        }
        
        .sidebar button:active {
            background-color: #2980b9;
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
        
        .brillo-icono {
            font-size: 16px;
            margin-right: 5px;
        }
        
        .habitacion-item {
            background-color: #34495e;
            border-radius: 5px;
            padding: 5px;
            margin: 2px 0;
        }
        
        .habitacion-item:hover {
            background-color: #3b5a7a;
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
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 14px;
        }
        
        .btn-color:hover {
            background-color: #f0f0f0;
            border-color: #9b59b6;
        }
        """
        
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def crear_interfaz(self):
        """Crea la interfaz principal de la aplicación"""
        # Panel principal horizontal
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.paned)
        
        # --- Sidebar izquierdo ---
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.sidebar.set_size_request(320, -1)
        self.sidebar.get_style_context().add_class("sidebar")
        
        # Título
        titulo = Gtk.Label()
        titulo.set_markup("<span size='x-large' weight='bold'>🏠 Philips Hue</span>")
        titulo.set_margin_top(20)
        titulo.set_margin_bottom(20)
        self.sidebar.pack_start(titulo, False, False, 0)
        
        # Frame de conexión
        frame_conexion = Gtk.Frame(label="🔌 Conexión")
        frame_conexion.set_margin_top(10)
        frame_conexion.set_margin_bottom(10)
        box_conexion = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box_conexion.set_margin_top(10)
        box_conexion.set_margin_bottom(10)
        box_conexion.set_margin_start(10)
        box_conexion.set_margin_end(10)
        
        # IP Entry con valor guardado
        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_placeholder_text("IP del puente Hue (ej: 192.168.1.100)")
        self.ip_entry.set_text(self.config.get("bridge_ip", "192.168.68.54"))
        self.ip_entry.set_margin_bottom(5)
        box_conexion.pack_start(self.ip_entry, False, False, 0)
        
        # Botón conectar
        self.btn_conectar = Gtk.Button(label="🔌 Conectar al puente")
        self.btn_conectar.connect("clicked", self.on_conectar_clicked)
        self.btn_conectar.set_margin_bottom(5)
        box_conexion.pack_start(self.btn_conectar, False, False, 0)
        
        # Estado de conexión
        self.label_estado = Gtk.Label()
        self.label_estado.set_markup("<span foreground='orange'>⚪ Estado: No conectado</span>")
        box_conexion.pack_start(self.label_estado, False, False, 0)
        
        frame_conexion.add(box_conexion)
        self.sidebar.pack_start(frame_conexion, False, False, 0)
        
        # Separador
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.sidebar.pack_start(separator, False, False, 10)
        
        # Lista de habitaciones
        self.scroll_habitaciones = Gtk.ScrolledWindow()
        self.scroll_habitaciones.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_habitaciones.set_min_content_height(400)
        
        self.lista_habitaciones = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.lista_habitaciones.set_margin_top(10)
        self.lista_habitaciones.set_margin_bottom(10)
        self.lista_habitaciones.set_margin_start(10)
        self.lista_habitaciones.set_margin_end(10)
        
        self.scroll_habitaciones.add(self.lista_habitaciones)
        
        label_habitaciones = Gtk.Label()
        label_habitaciones.set_markup("<span weight='bold'>🏠 Habitaciones y Zonas</span>")
        label_habitaciones.set_margin_bottom(10)
        self.sidebar.pack_start(label_habitaciones, False, False, 0)
        self.sidebar.pack_start(self.scroll_habitaciones, True, True, 0)
        
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
        self.nombre_habitacion_label.set_markup("<span size='x-large' weight='bold'>Selecciona una habitación o zona</span>")
        self.info_panel.pack_start(self.nombre_habitacion_label, False, False, 5)
        
        # Separador
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.panel_derecho.pack_start(separator2, False, False, 10)
        
        # Contenedor para escenas con borde azul
        self.escenas_frame = Gtk.Frame()
        self.escenas_frame.get_style_context().add_class("escenas-container")
        self.escenas_frame.set_label(" ESCENAS ")
        self.escenas_frame.set_label_align(0.5, 0.5)
        
        self.escenas_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.escenas_box.set_margin_top(15)
        self.escenas_box.set_margin_bottom(10)
        self.escenas_box.set_margin_start(10)
        self.escenas_box.set_margin_end(10)
        
        # Scroll horizontal para las escenas
        self.escenas_scroll = Gtk.ScrolledWindow()
        self.escenas_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.escenas_scroll.set_min_content_height(120)
        
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
        self.scroll_luces.set_min_content_height(500)
        
        self.contenedor_luces = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.contenedor_luces.set_margin_top(5)
        
        self.scroll_luces.add(self.contenedor_luces)
        self.panel_derecho.pack_start(self.scroll_luces, True, True, 0)
        
        self.paned.pack2(self.panel_derecho, True, False)
        
        # Variables para mantener referencia
        self.habitacion_actual = None
        self.botones_habitacion = {}
        self.switches_habitacion = {}  # Switches para cada habitación
        self.switches_luces = {}  # Switches para cada luz
        self.sliders_luces = {}  # Sliders para cada luz
        self.botones_color = {}  # Botones de color para cada luz
    
    def on_conectar_clicked(self, widget):
        """Maneja el click en el botón conectar"""
        ip = self.ip_entry.get_text().strip()
        if not ip:
            self.label_estado.set_markup("<span foreground='red'>❌ Error: Ingresa la IP del puente</span>")
            return
        
        # Guardar la IP en la configuración
        self.config["bridge_ip"] = ip
        self.guardar_configuracion()
        
        self.label_estado.set_markup("<span foreground='orange'>🔄 Conectando...</span>")
        self.btn_conectar.set_sensitive(False)
        self.spinner.start()
        
        threading.Thread(target=self.conectar_al_bridge, args=(ip,), daemon=True).start()
    
    def conectar_al_bridge(self, ip):
        """Conecta al bridge en un hilo separado"""
        try:
            bridge = Bridge(ip)
            bridge.get_api()
            self.bridge = bridge
            GLib.idle_add(self.conexion_exitosa)
        except Exception as e:
            GLib.idle_add(self.conexion_fallida, str(e))
    
    def conexion_exitosa(self):
        """Maneja la conexión exitosa"""
        self.label_estado.set_markup("<span foreground='green'>✅ Conectado al puente</span>")
        self.btn_conectar.set_sensitive(False)
        self.spinner.stop()
        self.spinner.hide()
        
        # Cargar grupos, luces y escenas
        threading.Thread(target=self.cargar_grupos_luces_y_escenas, daemon=True).start()
        return False
    
    def conexion_fallida(self, error_msg):
        """Maneja errores de conexión"""
        self.label_estado.set_markup(f"<span foreground='red'>❌ Error: {error_msg}</span>")
        self.btn_conectar.set_sensitive(True)
        self.spinner.stop()
        return False
    
    def detectar_soporte_color(self, luz_info):
        """Detecta si una luz soporta color basado en su información"""
        # Modelos que NO soportan color (blanco regulable)
        modelos_blanco = [
            'LWB001', 'LWB004', 'LWB006', 'LWB007', 'LWB010',
            'LTW001', 'LTW002', 'LTW003', 'LTW004', 'LTW005',
            'LWF001', 'LWF002', 'LWF003',
            'LWV001', 'LWV002',
            'LTP001', 'LTP002',
            'LDD001', 'LDD002',
            'LST001',
            'LLC001', 'LLC002', 'LLC003',
        ]
        
        # Modelos que SOPORTAN color (RGB)
        modelos_color = [
            'LCT001', 'LCT002', 'LCT003', 'LCT007', 'LCT010', 'LCT011', 'LCT012', 'LCT014', 'LCT015', 'LCT016',
            'LLC010', 'LLC011', 'LLC012', 'LLC013', 'LLC014',
            'LST002',
            '1742830P7', '1742930P7', '1743130P7', '1743230P7',
            '7602031P7', '7602032P7', '7602033P7', '7602034P7',
            'LCB001', 'LCB002',
            'LCP001', 'LCP002',
            'LCA001', 'LCA002', 'LCA003',
        ]
        
        model_id = luz_info.get('modelid', '')
        
        if model_id in modelos_color:
            return True
        
        if model_id in modelos_blanco:
            return False
        
        state = luz_info.get('state', {})
        
        if 'colormode' in state:
            colormode = state.get('colormode')
            if colormode in ['hs', 'xy']:
                return True
            if colormode == 'ct':
                return False
        
        product_name = luz_info.get('productname', '').lower()
        if 'color' in product_name and 'white' not in product_name:
            return True
        if 'rgb' in product_name:
            return True
        
        return False
    
    def cargar_grupos_luces_y_escenas(self):
        """Carga todos los grupos, sus luces y escenas"""
        try:
            self.luces = {}
            luces_por_nombre = {}
            self.luces_info = {}
            
            api_completa = self.bridge.get_api()
            
            if 'lights' in api_completa:
                for luz_id, luz_info in api_completa['lights'].items():
                    nombre_luz = luz_info.get('name')
                    model_id = luz_info.get('modelid', 'Desconocido')
                    has_color = self.detectar_soporte_color(luz_info)
                    
                    self.luces_info[nombre_luz] = {
                        'has_color': has_color,
                        'id': luz_id,
                        'model_id': model_id,
                        'info': luz_info
                    }
                    
                    color_icon = "🎨" if has_color else "⚪"
                    print(f"Luz: {nombre_luz} - Modelo: {model_id} - Color: {color_icon}")
            
            try:
                luces_por_nombre = self.bridge.get_light_objects('name')
                print(f"Luces encontradas por nombre: {len(luces_por_nombre)}")
                for nombre, luz_obj in luces_por_nombre.items():
                    self.luces[nombre] = luz_obj
            except Exception as e:
                print(f"Error obteniendo luces por nombre: {e}")
            
            id_v1_to_name = {}
            if 'lights' in api_completa:
                for luz_id_v1, luz_info in api_completa['lights'].items():
                    nombre_luz = luz_info.get('name')
                    if nombre_luz:
                        id_v1_to_name[luz_id_v1] = nombre_luz
            
            grupos_api = self.bridge.get_group()
            print(f"\nGrupos encontrados: {len(grupos_api)}")
            
            escenas_api = self.bridge.get_scene()
            print(f"Escenas encontradas: {len(escenas_api)}")
            
            self.grupos = {}
            self.escenas_por_grupo = {}
            luces_procesadas = set()
            
            for grupo_id, grupo_info in grupos_api.items():
                tipo_grupo = grupo_info.get('type', 'Unknown')
                nombre_grupo = grupo_info.get('name', f'Grupo {grupo_id}')
                
                print(f"\nProcesando {tipo_grupo}: {nombre_grupo}")
                
                if tipo_grupo in ['Room', 'Zone', 'LightGroup']:
                    luces_grupo = []
                    lights_ids = grupo_info.get('lights', [])
                    
                    for luz_id in lights_ids:
                        luz_id_str = str(luz_id)
                        nombre_luz = None
                        luz_obj = None
                        
                        if luz_id_str in id_v1_to_name:
                            nombre_luz = id_v1_to_name[luz_id_str]
                            if nombre_luz in self.luces:
                                luz_obj = self.luces[nombre_luz]
                        
                        if luz_obj and nombre_luz:
                            tiene_color = self.luces_info.get(nombre_luz, {}).get('has_color', False)
                            luces_grupo.append({
                                'id': luz_id_str,
                                'objeto': luz_obj,
                                'nombre': nombre_luz,
                                'has_color': tiene_color
                            })
                            luces_procesadas.add(nombre_luz)
                            color_status = "🎨" if tiene_color else "⚪"
                            print(f"  - Luz: {nombre_luz} {color_status}")
                    
                    if luces_grupo:
                        icono = "🏠" if tipo_grupo == 'Room' else "📍" if tipo_grupo == 'Zone' else "💡"
                        self.grupos[grupo_id] = {
                            'nombre': nombre_grupo,
                            'luces': luces_grupo,
                            'tipo': tipo_grupo,
                            'icono': icono,
                            'group_id': grupo_id
                        }
                        
                        escenas_grupo = []
                        for scene_id, scene_info in escenas_api.items():
                            scene_group = scene_info.get('group')
                            if scene_group == nombre_grupo or str(scene_group) == str(grupo_id):
                                escenas_grupo.append({
                                    'id': scene_id,
                                    'name': scene_info.get('name', 'Sin nombre'),
                                    'icon': self.obtener_icono_escena(scene_info.get('name', ''))
                                })
                        
                        if escenas_grupo:
                            self.escenas_por_grupo[grupo_id] = escenas_grupo
                            print(f"  ✓ {len(escenas_grupo)} escenas cargadas para {nombre_grupo}")
            
            self.luces_sin_grupo = []
            for nombre_luz, luz_obj in self.luces.items():
                if nombre_luz not in luces_procesadas:
                    tiene_color = self.luces_info.get(nombre_luz, {}).get('has_color', False)
                    self.luces_sin_grupo.append({
                        'id': nombre_luz,
                        'objeto': luz_obj,
                        'nombre': nombre_luz,
                        'has_color': tiene_color
                    })
            
            if self.luces_sin_grupo:
                self.grupos['sin_grupo'] = {
                    'nombre': '📦 Otras luces',
                    'luces': self.luces_sin_grupo,
                    'tipo': 'Unassigned',
                    'icono': '🔆',
                    'group_id': None
                }
            
            print(f"\n=== RESUMEN FINAL ===")
            print(f"Total de grupos con luces: {len(self.grupos)}")
            print(f"Total de grupos con escenas: {len(self.escenas_por_grupo)}")
            
            luces_color = [nombre for nombre, info in self.luces_info.items() if info.get('has_color', False)]
            print(f"Luces con soporte de color ({len(luces_color)}): {', '.join(luces_color)}")
            
            if not self.grupos:
                GLib.idle_add(self.mostrar_error, "No se encontraron grupos con luces")
                GLib.idle_add(self.limpiar_interfaz_sin_habitaciones)
                return
            
            GLib.idle_add(self.actualizar_interfaz_grupos)
            
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            import traceback
            traceback.print_exc()
            GLib.idle_add(self.mostrar_error, f"Error al cargar datos: {str(e)}")
    
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
    
    def limpiar_interfaz_sin_habitaciones(self):
        """Limpia la interfaz cuando no hay habitaciones"""
        for child in self.lista_habitaciones.get_children():
            self.lista_habitaciones.remove(child)
        
        label_no_grupos = Gtk.Label()
        label_no_grupos.set_markup("<span foreground='orange'>⚠️ No se encontraron grupos con luces\n\nVerifica la configuración en la app de Hue</span>")
        label_no_grupos.set_margin_top(20)
        self.lista_habitaciones.pack_start(label_no_grupos, False, False, 0)
        self.lista_habitaciones.show_all()
        
        for child in self.contenedor_luces.get_children():
            self.contenedor_luces.remove(child)
        
        self.nombre_habitacion_label.set_markup("<span size='x-large' weight='bold'>No hay grupos disponibles</span>")
    
    def actualizar_interfaz_grupos(self):
        """Actualiza el sidebar con la lista de habitaciones y sus switches"""
        for child in self.lista_habitaciones.get_children():
            self.lista_habitaciones.remove(child)
        
        if not self.grupos:
            return
        
        self.botones_habitacion = {}
        self.switches_habitacion = {}
        
        def ordenar_grupo(item):
            grupo_id, grupo = item
            prioridad = 2
            if grupo['tipo'] == 'Room':
                prioridad = 0
            elif grupo['tipo'] == 'Zone':
                prioridad = 1
            return (prioridad, grupo['nombre'])
        
        grupos_ordenados = sorted(self.grupos.items(), key=ordenar_grupo)
        
        for grupo_id, grupo in grupos_ordenados:
            contenedor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            contenedor.set_margin_bottom(3)
            contenedor.get_style_context().add_class("habitacion-item")
            
            btn_habitacion = Gtk.Button(label=f"{grupo['icono']} {grupo['nombre']} ({len(grupo['luces'])} luces)")
            btn_habitacion.connect("clicked", self.on_habitacion_seleccionada, grupo_id, grupo['nombre'])
            btn_habitacion.set_halign(Gtk.Align.START)
            btn_habitacion.set_valign(Gtk.Align.CENTER)
            btn_habitacion.set_hexpand(True)
            btn_habitacion.set_property("can-focus", False)
            
            # CORREGIDO: El switch debe estar encendido si al menos una luz está encendida
            alguna_encendida = any(luz['objeto'].on for luz in grupo['luces']) if grupo['luces'] else False
            switch = Gtk.Switch()
            switch.set_active(alguna_encendida)
            switch.set_halign(Gtk.Align.END)
            switch.set_valign(Gtk.Align.CENTER)
            switch.set_tooltip_text(f"Encender/Apagar todas las luces de {grupo['nombre']}")
            switch.connect("notify::active", self.on_habitacion_switch_toggled, grupo_id)
            
            contenedor.pack_start(btn_habitacion, True, True, 0)
            contenedor.pack_start(switch, False, False, 0)
            
            self.lista_habitaciones.pack_start(contenedor, False, False, 0)
            
            self.botones_habitacion[grupo_id] = btn_habitacion
            self.switches_habitacion[grupo_id] = switch
        
        self.lista_habitaciones.show_all()
        
        if self.grupos:
            primer_grupo = list(self.grupos.keys())[0]
            self.on_habitacion_seleccionada(None, primer_grupo, self.grupos[primer_grupo]['nombre'])
    
    def on_habitacion_switch_toggled(self, switch, gparam, grupo_id):
        """Maneja el cambio del switch de la habitación"""
        if grupo_id not in self.grupos:
            return
        
        grupo = self.grupos[grupo_id]
        nuevo_estado = switch.get_active()
        
        if not grupo['luces']:
            switch.set_active(False)
            return
        
        try:
            # Si el switch se activa, encender todas las luces
            # Si el switch se desactiva, apagar todas las luces
            for luz in grupo['luces']:
                luz['objeto'].on = nuevo_estado
            
            # Actualizar los switches individuales sin disparar eventos
            if self.habitacion_actual == grupo_id:
                for luz in grupo['luces']:
                    if luz['objeto'] in self.switches_luces:
                        luz_switch = self.switches_luces[luz['objeto']]
                        luz_switch.handler_block_by_func(self.on_luz_switch_toggled)
                        luz_switch.set_active(nuevo_estado)
                        luz_switch.handler_unblock_by_func(self.on_luz_switch_toggled)
                    
                    if luz['objeto'] in self.sliders_luces:
                        if nuevo_estado:
                            valor_hue = luz['objeto'].brightness if luz['objeto'].brightness else 254
                            valor_porcentaje = int((valor_hue / 254) * 100)
                            self.sliders_luces[luz['objeto']].set_value(valor_porcentaje)
                            self.sliders_luces[luz['objeto']].set_sensitive(True)
                        else:
                            self.sliders_luces[luz['objeto']].set_value(0)
                            self.sliders_luces[luz['objeto']].set_sensitive(False)
            
        except Exception as e:
            self.mostrar_error(f"Error al controlar habitación: {e}")
            switch.set_active(not nuevo_estado)
    
    def on_habitacion_seleccionada(self, widget, grupo_id, nombre_grupo):
        """Muestra los controles de la habitación seleccionada"""
        self.habitacion_actual = grupo_id
        grupo = self.grupos[grupo_id]
        
        # Actualizar título
        self.actualizar_titulo_habitacion(grupo)
        
        # Cargar escenas
        self.cargar_escenas(grupo_id)
        
        # Cargar luces
        self.cargar_luces_habitacion(grupo['luces'])
    
    def actualizar_titulo_habitacion(self, grupo):
        """Actualiza el título de la habitación en el panel derecho"""
        tipo_texto = ""
        if grupo['tipo'] == 'Room':
            tipo_texto = "Habitación"
        elif grupo['tipo'] == 'Zone':
            tipo_texto = "Zona"
        elif grupo['tipo'] == 'Unassigned':
            tipo_texto = "Luces sin grupo"
        else:
            tipo_texto = "Grupo"
        
        self.nombre_habitacion_label.set_markup(
            f"<span size='x-large' weight='bold'>{grupo['icono']} {grupo['nombre']}</span>\n"
            f"<span size='small'>{tipo_texto} con {len(grupo['luces'])} luces</span>"
        )
    
    def cargar_escenas(self, grupo_id):
        """Carga las escenas para el grupo seleccionado"""
        for child in self.escenas_container.get_children():
            self.escenas_container.remove(child)
        
        if grupo_id in self.escenas_por_grupo and self.escenas_por_grupo[grupo_id]:
            escenas = self.escenas_por_grupo[grupo_id]
            
            for escena in escenas:
                self.crear_boton_escena(escena, grupo_id)
            
            self.escenas_frame.show()
        else:
            self.escenas_frame.hide()
        
        self.escenas_container.show_all()
    
    def crear_boton_escena(self, escena, grupo_id):
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
        btn.connect("clicked", self.on_escena_clicked, escena['id'], grupo_id)
        
        self.escenas_container.pack_start(btn, False, False, 0)
    
    def on_escena_clicked(self, widget, scene_id, grupo_id):
        """Aplica una escena seleccionada"""
        try:
            grupo = self.grupos.get(grupo_id)
            if not grupo:
                return
            
            self.bridge.activate_scene(grupo['nombre'], scene_id)
            print(f"Escena activada: {scene_id} en {grupo['nombre']}")
            
            if self.habitacion_actual == grupo_id:
                GLib.timeout_add(500, self.actualizar_despues_escena, grupo_id)
            
        except Exception as e:
            self.mostrar_error(f"Error al aplicar escena: {e}")
    
    def actualizar_despues_escena(self, grupo_id):
        """Actualiza la interfaz después de aplicar una escena"""
        if grupo_id in self.grupos:
            grupo = self.grupos[grupo_id]
            
            # Actualizar switches individuales sin disparar eventos
            for luz in grupo['luces']:
                if luz['objeto'] in self.switches_luces:
                    luz_switch = self.switches_luces[luz['objeto']]
                    luz_switch.handler_block_by_func(self.on_luz_switch_toggled)
                    luz_switch.set_active(luz['objeto'].on)
                    luz_switch.handler_unblock_by_func(self.on_luz_switch_toggled)
                
                if luz['objeto'] in self.sliders_luces:
                    if luz['objeto'].on:
                        valor_hue = luz['objeto'].brightness if luz['objeto'].brightness else 254
                        valor_porcentaje = int((valor_hue / 254) * 100)
                        self.sliders_luces[luz['objeto']].set_value(valor_porcentaje)
                        self.sliders_luces[luz['objeto']].set_sensitive(True)
                    else:
                        self.sliders_luces[luz['objeto']].set_value(0)
                        self.sliders_luces[luz['objeto']].set_sensitive(False)
            
            # CORREGIDO: Actualizar switch de la habitación
            # Debe estar encendido si al menos una luz está encendida
            if grupo_id in self.switches_habitacion:
                habitacion_switch = self.switches_habitacion[grupo_id]
                alguna_encendida = any(luz['objeto'].on for luz in grupo['luces'])
                habitacion_switch.handler_block_by_func(self.on_habitacion_switch_toggled)
                habitacion_switch.set_active(alguna_encendida)
                habitacion_switch.handler_unblock_by_func(self.on_habitacion_switch_toggled)
        
        return False
    
    def cargar_luces_habitacion(self, luces):
        """Carga los controles para cada luz de la habitación"""
        for child in self.contenedor_luces.get_children():
            self.contenedor_luces.remove(child)
        
        self.switches_luces = {}
        self.sliders_luces = {}
        self.botones_color = {}
        
        if not luces:
            label_no_luces = Gtk.Label()
            label_no_luces.set_markup("<span foreground='gray'>📭 No hay luces en este grupo</span>")
            label_no_luces.set_margin_top(50)
            self.contenedor_luces.pack_start(label_no_luces, False, False, 0)
        else:
            for luz in luces:
                self.crear_control_luz(luz)
        
        self.contenedor_luces.show_all()
    
    def crear_control_luz(self, luz):
        """Crea un widget de control para una luz individual"""
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        card.get_style_context().add_class("card-luz")
        card.set_margin_bottom(2)
        
        # Nombre de la luz
        nombre = Gtk.Label()
        nombre_texto = f"<b>{luz['nombre']}</b>"
        nombre.set_markup(nombre_texto)
        nombre.get_style_context().add_class("nombre-luz")
        nombre.set_halign(Gtk.Align.START)
        nombre.set_size_request(150, -1)
        card.pack_start(nombre, False, False, 0)
        
        # Icono de brillo
        brillo_icono = Gtk.Label()
        brillo_icono.set_markup("💡")
        brillo_icono.get_style_context().add_class("brillo-icono")
        brillo_icono.set_tooltip_text("Brillo")
        card.pack_start(brillo_icono, False, False, 0)
        
        # Slider de brillo
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        
        try:
            valor_hue = luz['objeto'].brightness if luz['objeto'].on else 0
            valor_porcentaje = int((valor_hue / 254) * 100) if valor_hue > 0 else 0
        except:
            valor_porcentaje = 0
        
        slider.set_value(valor_porcentaje)
        slider.set_digits(0)
        slider.set_hexpand(True)
        slider.set_vexpand(False)
        slider.set_sensitive(luz['objeto'].on)
        slider.get_style_context().add_class("slider")
        slider.connect("value-changed", self.on_brillo_changed, luz['objeto'])
        card.pack_start(slider, True, True, 0)
        
        # Valor del brillo en porcentaje
        valor_brillo = Gtk.Label(label=f"{valor_porcentaje}%")
        valor_brillo.set_width_chars(4)
        valor_brillo.set_halign(Gtk.Align.CENTER)
        slider.connect("value-changed", self.actualizar_label_brillo, valor_brillo)
        card.pack_start(valor_brillo, False, False, 0)
        
        # Botón de selector de color (solo si la luz soporta color)
        if luz['has_color']:
            btn_color = Gtk.Button(label="🎨")
            btn_color.set_tooltip_text("Seleccionar color")
            btn_color.get_style_context().add_class("btn-color")
            btn_color.set_size_request(40, -1)
            btn_color.connect("clicked", self.on_color_clicked, luz['objeto'])
            card.pack_start(btn_color, False, False, 0)
            self.botones_color[luz['objeto']] = btn_color
        
        # Switch de encendido/apagado
        switch = Gtk.Switch()
        switch.set_active(luz['objeto'].on)
        switch.set_halign(Gtk.Align.END)
        switch.set_valign(Gtk.Align.CENTER)
        switch.connect("notify::active", self.on_luz_switch_toggled, luz['objeto'])
        card.pack_start(switch, False, False, 0)
        
        self.contenedor_luces.pack_start(card, False, False, 0)
        
        self.switches_luces[luz['objeto']] = switch
        self.sliders_luces[luz['objeto']] = slider
    
    def on_luz_switch_toggled(self, switch, gparam, luz):
        """Maneja el cambio de estado del switch de una luz individual"""
        try:
            nuevo_estado = switch.get_active()
            luz.on = nuevo_estado
            
            if luz in self.sliders_luces:
                self.sliders_luces[luz].set_sensitive(nuevo_estado)
            
            if not nuevo_estado and luz in self.sliders_luces:
                self.sliders_luces[luz].set_value(0)
            elif nuevo_estado and luz in self.sliders_luces:
                valor_hue = luz.brightness if luz.brightness else 254
                valor_porcentaje = int((valor_hue / 254) * 100)
                self.sliders_luces[luz].set_value(valor_porcentaje)
            
            # CORREGIDO: Actualizar el switch de la habitación
            # Debe estar encendido si al menos una luz está encendida
            if self.habitacion_actual and self.habitacion_actual in self.grupos:
                grupo = self.grupos[self.habitacion_actual]
                alguna_encendida = any(luz_obj['objeto'].on for luz_obj in grupo['luces'])
                
                if self.habitacion_actual in self.switches_habitacion:
                    habitacion_switch = self.switches_habitacion[self.habitacion_actual]
                    habitacion_switch.handler_block_by_func(self.on_habitacion_switch_toggled)
                    habitacion_switch.set_active(alguna_encendida)
                    habitacion_switch.handler_unblock_by_func(self.on_habitacion_switch_toggled)
            
        except Exception as e:
            self.mostrar_error(f"Error al cambiar estado: {e}")
            switch.set_active(not nuevo_estado)
    
    def on_color_clicked(self, widget, luz):
        """Abre un selector de color para la luz"""
        try:
            dialog = Gtk.ColorChooserDialog(title="Seleccionar color para la luz", parent=self)
            
            try:
                if hasattr(luz, 'xy') and luz.xy:
                    x, y = luz.xy
                    r, g, b = self.xy_to_rgb(x, y)
                    color = Gdk.RGBA()
                    color.red = r
                    color.green = g
                    color.blue = b
                    color.alpha = 1.0
                    dialog.set_rgba(color)
            except:
                pass
            
            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                color = dialog.get_rgba()
                self.aplicar_color(luz, color)
            
            dialog.destroy()
            
        except Exception as e:
            self.mostrar_error(f"Error al seleccionar color: {e}")
    
    def xy_to_rgb(self, x, y):
        """Convierte coordenadas xy de Hue a RGB"""
        z = 1.0 - x - y
        Y = 1.0
        X = (Y / y) * x
        Z = (Y / y) * z
        
        r = X * 1.656492 - Y * 0.354851 - Z * 0.255038
        g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152
        b = X * 0.051713 - Y * 0.121364 + Z * 1.011530
        
        r = max(0, min(1, r))
        g = max(0, min(1, g))
        b = max(0, min(1, b))
        
        return r, g, b
    
    def rgb_to_xy(self, r, g, b):
        """Convierte RGB a coordenadas xy para Hue"""
        r = self.gamma_correction(r)
        g = self.gamma_correction(g)
        b = self.gamma_correction(b)
        
        X = r * 0.664511 + g * 0.154324 + b * 0.162028
        Y = r * 0.283881 + g * 0.668433 + b * 0.047685
        Z = r * 0.000088 + g * 0.072310 + b * 0.986039
        
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
    
    def aplicar_color(self, luz, color):
        """Aplica el color seleccionado a la luz"""
        try:
            if not luz.on:
                luz.on = True
                if luz in self.switches_luces:
                    self.switches_luces[luz].set_active(True)
            
            x, y = self.rgb_to_xy(color.red, color.green, color.blue)
            luz.xy = [x, y]
            
            print(f"Color aplicado a la luz")
            
        except Exception as e:
            self.mostrar_error(f"Error al aplicar color: {e}")
    
    def on_brillo_changed(self, widget, luz):
        """Cambia el brillo de una luz"""
        try:
            porcentaje = int(widget.get_value())
            valor_hue = int((porcentaje / 100) * 254)
            if luz.on:
                luz.brightness = valor_hue
        except Exception as e:
            pass
    
    def actualizar_label_brillo(self, widget, label):
        """Actualiza el label que muestra el valor del brillo en porcentaje"""
        valor = int(widget.get_value())
        label.set_label(f"{valor}%")
    
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

def main():
    """Punto de entrada principal"""
    app = AppHueMejorada()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()
    
    
    
