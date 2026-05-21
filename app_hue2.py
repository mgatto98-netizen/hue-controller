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
            "bridge_ip": "192.168.68.54"  # IP por defecto
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
            border-radius: 10px;
            padding: 15px;
            margin: 10px;
            border: 1px solid #bdc3c7;
            transition: all 0.3s ease;
        }
        
        .card-luz:hover {
            background-color: #e0e4e5;
            border-color: #3498db;
        }
        
        .nombre-luz {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .btn-encender {
            background-color: #27ae60;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
        }
        
        .btn-encender:hover {
            background-color: #229954;
        }
        
        .btn-apagar {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
        }
        
        .btn-apagar:hover {
            background-color: #c0392b;
        }
        
        .btn-habitacion {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        }
        
        .btn-habitacion:hover {
            background-color: #2980b9;
        }
        
        .info-panel {
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        .slider {
            margin: 5px;
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
        self.sidebar.set_size_request(280, -1)
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
        self.ip_entry.set_text(self.config.get("bridge_ip", "192.168.1.100"))
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
        
        self.lista_habitaciones = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
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
        
        # Botón para controlar toda la habitación
        self.btn_control_habitacion = Gtk.Button(label="🔆 Encender todas las luces")
        self.btn_control_habitacion.get_style_context().add_class("btn-habitacion")
        self.btn_control_habitacion.connect("clicked", self.on_control_habitacion_clicked)
        self.btn_control_habitacion.set_sensitive(False)
        self.info_panel.pack_start(self.btn_control_habitacion, False, False, 10)
        
        # Separador
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.panel_derecho.pack_start(separator2, False, False, 10)
        
        # Scroll para las luces
        self.scroll_luces = Gtk.ScrolledWindow()
        self.scroll_luces.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll_luces.set_min_content_height(500)
        
        self.contenedor_luces = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.contenedor_luces.set_margin_top(10)
        
        self.scroll_luces.add(self.contenedor_luces)
        self.panel_derecho.pack_start(self.scroll_luces, True, True, 0)
        
        self.paned.pack2(self.panel_derecho, True, False)
        
        # Variables para mantener referencia
        self.habitacion_actual = None
        self.botones_habitacion = {}
    
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
        
        # Cargar grupos y luces
        threading.Thread(target=self.cargar_grupos_y_luces, daemon=True).start()
        return False
    
    def conexion_fallida(self, error_msg):
        """Maneja errores de conexión"""
        self.label_estado.set_markup(f"<span foreground='red'>❌ Error: {error_msg}</span>")
        self.btn_conectar.set_sensitive(True)
        self.spinner.stop()
        return False
    
    def cargar_grupos_y_luces(self):
        """Carga todos los grupos (habitaciones y zonas) y sus luces"""
        try:
            # Obtener todas las luces
            self.luces = {}
            luces_por_nombre = {}
            
            # Obtener luces por nombre (más confiable)
            try:
                luces_por_nombre = self.bridge.get_light_objects('name')
                print(f"Luces encontradas por nombre: {len(luces_por_nombre)}")
                for nombre, luz_obj in luces_por_nombre.items():
                    self.luces[nombre] = luz_obj
                    print(f"  - Luz: {nombre}")
            except Exception as e:
                print(f"Error obteniendo luces por nombre: {e}")
            
            # Obtener la API completa para tener los IDs
            api_completa = self.bridge.get_api()
            
            # Crear mapeo de ID V1 a nombre de luz
            id_v1_to_name = {}
            if 'lights' in api_completa:
                for luz_id_v1, luz_info in api_completa['lights'].items():
                    nombre_luz = luz_info.get('name')
                    if nombre_luz:
                        id_v1_to_name[luz_id_v1] = nombre_luz
                        print(f"  Mapeo ID V1 {luz_id_v1} -> {nombre_luz}")
            
            # Obtener grupos
            grupos_api = self.bridge.get_group()
            print(f"\nGrupos encontrados: {len(grupos_api)}")
            
            self.grupos = {}
            luces_procesadas = set()
            
            # Procesar cada grupo
            for grupo_id, grupo_info in grupos_api.items():
                tipo_grupo = grupo_info.get('type', 'Unknown')
                nombre_grupo = grupo_info.get('name', f'Grupo {grupo_id}')
                
                print(f"\nProcesando {tipo_grupo}: {nombre_grupo}")
                
                # Incluir Room, Zone y LightGroup
                if tipo_grupo in ['Room', 'Zone', 'LightGroup']:
                    luces_grupo = []
                    
                    # Obtener los IDs de las luces en este grupo
                    lights_ids = grupo_info.get('lights', [])
                    print(f"  IDs de luces en el grupo: {lights_ids}")
                    
                    for luz_id in lights_ids:
                        luz_id_str = str(luz_id)
                        nombre_luz = None
                        luz_obj = None
                        
                        # Buscar por ID V1
                        if luz_id_str in id_v1_to_name:
                            nombre_luz = id_v1_to_name[luz_id_str]
                            if nombre_luz in self.luces:
                                luz_obj = self.luces[nombre_luz]
                        
                        # Si no se encuentra, buscar por el ID directamente en la API
                        if not luz_obj:
                            try:
                                # Intentar obtener información de la luz específica
                                luz_info = self.bridge.get_light(luz_id_str)
                                if luz_info:
                                    nombre_luz = luz_info.get('name')
                                    if nombre_luz and nombre_luz in self.luces:
                                        luz_obj = self.luces[nombre_luz]
                            except:
                                pass
                        
                        if luz_obj and nombre_luz:
                            luces_grupo.append({
                                'id': luz_id_str,
                                'objeto': luz_obj,
                                'nombre': nombre_luz
                            })
                            luces_procesadas.add(nombre_luz)
                            print(f"  ✓ Luz encontrada: {nombre_luz} (ID: {luz_id_str})")
                        else:
                            print(f"  ✗ Luz no encontrada para ID: {luz_id_str}")
                    
                    if luces_grupo:
                        icono = "🏠" if tipo_grupo == 'Room' else "📍" if tipo_grupo == 'Zone' else "💡"
                        self.grupos[grupo_id] = {
                            'nombre': nombre_grupo,
                            'luces': luces_grupo,
                            'tipo': tipo_grupo,
                            'icono': icono
                        }
                        print(f"  ✓ {tipo_grupo} añadida: {nombre_grupo} con {len(luces_grupo)} luces")
                    else:
                        print(f"  ✗ {tipo_grupo} sin luces asignadas, omitida")
            
            # Encontrar luces que no están en ningún grupo
            self.luces_sin_grupo = []
            for nombre_luz, luz_obj in self.luces.items():
                if nombre_luz not in luces_procesadas:
                    self.luces_sin_grupo.append({
                        'id': nombre_luz,
                        'objeto': luz_obj,
                        'nombre': nombre_luz
                    })
                    print(f"Luz sin grupo: {nombre_luz}")
            
            # Si hay luces sin grupo, crear una categoría
            if self.luces_sin_grupo:
                self.grupos['sin_grupo'] = {
                    'nombre': '📦 Otras luces',
                    'luces': self.luces_sin_grupo,
                    'tipo': 'Unassigned',
                    'icono': '🔆'
                }
                print(f"\n✓ Creado grupo 'Otras luces' con {len(self.luces_sin_grupo)} luces")
            
            print(f"\n=== RESUMEN FINAL ===")
            print(f"Total de grupos con luces: {len(self.grupos)}")
            for grupo_id, grupo in self.grupos.items():
                print(f"  - {grupo['icono']} {grupo['nombre']}: {len(grupo['luces'])} luces")
            
            if not self.grupos:
                print("No se encontraron grupos con luces")
                GLib.idle_add(self.mostrar_error, 
                            "No se encontraron grupos con luces en el puente.\n\n"
                            "Verifica que:\n"
                            "1. Hayas presionado el botón físico del puente\n"
                            "2. Tengas habitaciones configuradas en la app de Hue\n"
                            "3. Las habitaciones tengan luces asignadas")
                GLib.idle_add(self.limpiar_interfaz_sin_habitaciones)
                return
            
            GLib.idle_add(self.actualizar_interfaz_grupos)
            
        except Exception as e:
            print(f"Error al cargar grupos: {e}")
            import traceback
            traceback.print_exc()
            GLib.idle_add(self.mostrar_error, f"Error al cargar grupos: {str(e)}")
    
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
        self.btn_control_habitacion.set_sensitive(False)
    
    def actualizar_interfaz_grupos(self):
        """Actualiza el sidebar con la lista de habitaciones y zonas"""
        # Limpiar lista de habitaciones
        for child in self.lista_habitaciones.get_children():
            self.lista_habitaciones.remove(child)
        
        if not self.grupos:
            return
        
        self.botones_habitacion = {}
        
        # Ordenar grupos por prioridad y nombre
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
            btn = Gtk.Button(label=f"{grupo['icono']} {grupo['nombre']} ({len(grupo['luces'])} luces)")
            btn.connect("clicked", self.on_habitacion_seleccionada, grupo_id, grupo['nombre'])
            btn.set_halign(Gtk.Align.START)
            btn.set_valign(Gtk.Align.CENTER)
            btn.set_margin_bottom(5)
            self.lista_habitaciones.pack_start(btn, False, False, 0)
            self.botones_habitacion[grupo_id] = btn
        
        self.lista_habitaciones.show_all()
        
        # Seleccionar la primera habitación
        if self.grupos:
            primer_grupo = list(self.grupos.keys())[0]
            self.on_habitacion_seleccionada(None, primer_grupo, self.grupos[primer_grupo]['nombre'])
    
    def on_habitacion_seleccionada(self, widget, grupo_id, nombre_grupo):
        """Muestra los controles de la habitación seleccionada"""
        self.habitacion_actual = grupo_id
        grupo = self.grupos[grupo_id]
        
        # Actualizar título
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
            f"<span size='x-large' weight='bold'>{grupo['icono']} {nombre_grupo}</span>\n"
            f"<span size='small'>{tipo_texto} con {len(grupo['luces'])} luces</span>"
        )
        
        # Actualizar botón de control
        self.btn_control_habitacion.set_sensitive(True)
        self.actualizar_boton_habitacion(grupo)
        
        # Cargar luces
        self.cargar_luces_habitacion(grupo['luces'])
    
    def actualizar_boton_habitacion(self, grupo):
        """Actualiza el texto del botón según el estado de las luces"""
        if not grupo['luces']:
            self.btn_control_habitacion.set_label("🔆 Sin luces")
            self.btn_control_habitacion.set_sensitive(False)
            return
            
        todas_encendidas = all(luz['objeto'].on for luz in grupo['luces'])
        if todas_encendidas:
            self.btn_control_habitacion.set_label("🔴 Apagar todas las luces")
        else:
            self.btn_control_habitacion.set_label("🟢 Encender todas las luces")
    
    def cargar_luces_habitacion(self, luces):
        """Carga los controles para cada luz de la habitación"""
        # Limpiar contenedor
        for child in self.contenedor_luces.get_children():
            self.contenedor_luces.remove(child)
        
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
        # Card contenedora
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.get_style_context().add_class("card-luz")
        card.set_margin_bottom(5)
        
        # Fila superior: nombre y botones
        fila_superior = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Nombre de la luz
        nombre = Gtk.Label()
        nombre.set_markup(f"<span size='large' weight='bold'>💡 {luz['nombre']}</span>")
        nombre.get_style_context().add_class("nombre-luz")
        fila_superior.pack_start(nombre, True, True, 0)
        
        # Botón de encendido/apagado
        btn_on_off = Gtk.Button()
        if luz['objeto'].on:
            btn_on_off.set_label("🔴 Apagar")
            btn_on_off.get_style_context().add_class("btn-apagar")
        else:
            btn_on_off.set_label("🟢 Encender")
            btn_on_off.get_style_context().add_class("btn-encender")
        
        btn_on_off.connect("clicked", self.on_toggle_luz, luz['objeto'], btn_on_off)
        fila_superior.pack_start(btn_on_off, False, False, 0)
        
        card.pack_start(fila_superior, False, False, 0)
        
        # Fila inferior: control de brillo
        fila_brillo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        label_brillo = Gtk.Label(label="💡 Brillo:")
        fila_brillo.pack_start(label_brillo, False, False, 0)
        
        # Slider de brillo
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 254, 1)
        try:
            valor_actual = luz['objeto'].brightness if luz['objeto'].on else 0
        except:
            valor_actual = 0
        slider.set_value(valor_actual)
        slider.set_digits(0)
        slider.set_hexpand(True)
        slider.get_style_context().add_class("slider")
        slider.connect("value-changed", self.on_brillo_changed, luz['objeto'])
        
        fila_brillo.pack_start(slider, True, True, 0)
        
        # Valor del brillo
        valor_brillo = Gtk.Label(label=f"{int(valor_actual)}%")
        valor_brillo.set_width_chars(5)
        fila_brillo.pack_start(valor_brillo, False, False, 0)
        
        slider.connect("value-changed", self.actualizar_label_brillo, valor_brillo)
        
        card.pack_start(fila_brillo, False, False, 0)
        
        self.contenedor_luces.pack_start(card, False, False, 0)
    
    def on_toggle_luz(self, widget, luz, btn_widget):
        """Alterna el estado de una luz"""
        try:
            if luz.on:
                luz.on = False
                btn_widget.set_label("🟢 Encender")
                btn_widget.get_style_context().remove_class("btn-apagar")
                btn_widget.get_style_context().add_class("btn-encender")
            else:
                luz.on = True
                btn_widget.set_label("🔴 Apagar")
                btn_widget.get_style_context().remove_class("btn-encender")
                btn_widget.get_style_context().add_class("btn-apagar")
            
            # Actualizar botón de habitación
            if self.habitacion_actual and self.habitacion_actual in self.grupos:
                grupo = self.grupos[self.habitacion_actual]
                self.actualizar_boton_habitacion(grupo)
                
        except Exception as e:
            self.mostrar_error(f"Error al cambiar estado: {e}")
    
    def on_brillo_changed(self, widget, luz):
        """Cambia el brillo de una luz"""
        try:
            nuevo_brillo = int(widget.get_value())
            if luz.on:
                luz.brightness = nuevo_brillo
        except Exception as e:
            pass
    
    def actualizar_label_brillo(self, widget, label):
        """Actualiza el label que muestra el valor del brillo"""
        valor = int(widget.get_value())
        label.set_label(f"{valor}%")
    
    def on_control_habitacion_clicked(self, widget):
        """Controla todas las luces de la habitación actual"""
        if not self.habitacion_actual or self.habitacion_actual not in self.grupos:
            return
        
        grupo = self.grupos[self.habitacion_actual]
        
        if not grupo['luces']:
            return
            
        todas_encendidas = all(luz['objeto'].on for luz in grupo['luces'])
        
        try:
            nuevo_estado = not todas_encendidas
            
            for luz in grupo['luces']:
                luz['objeto'].on = nuevo_estado
            
            # Actualizar interfaz
            self.actualizar_boton_habitacion(grupo)
            self.cargar_luces_habitacion(grupo['luces'])
            
        except Exception as e:
            self.mostrar_error(f"Error al controlar habitación: {e}")
    
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
