#!/usr/bin/env python3
# app_hue_mejorada.py
# Aplicación para controlar luces Philips Hue en Linux

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

class AppHueMejorada(Gtk.Window):
    def __init__(self):
        super().__init__(title="Philips Hue Controller - Control de Luces y Sensores")
        
        # Configuración de la ventana
        self.set_default_size(1200, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(400, 300) 
        self.set_resizable(True)  
        # Variables
        self.bridge_ip = None
        self.api_key = None
        self.headers = None
        
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
        
        # Estilo CSS
        self.aplicar_estilos()
        
        # Crear la interfaz
        self.crear_interfaz()
        
        # Si hay IP y API Key guardadas, intentar conectar automáticamente
        if self.config.get("bridge_ip") and self.config.get("api_key"):
            GLib.idle_add(lambda: self.on_conectar_clicked(None))
        
        self.show_all()
    
    def cargar_configuracion(self):
        """Carga la configuración guardada"""
        config_default = {
            "bridge_ip": "",
            "api_key": "",
            "update_interval": 300,
            "app_name": "hue_controller_linux"
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
        
        .sensor-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 10px;
            margin: 5px;
            color: white;
            min-width: 160px;
        }
        
        .sensor-temperatura {
            font-size: 32px;
            font-weight: bold;
        }
        
        .sensor-ubicacion {
            font-size: 14px;
            font-weight: bold;
        }
        
        .sensor-updated {
            font-size: 10px;
            margin-top: 5px;
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
        self.sidebar.set_size_request(380, -1)
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
        
        # IP Entry
        ip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ip_box.pack_start(Gtk.Label(label="IP del puente:"), False, False, 0)
        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_placeholder_text("192.168.68.54")
        self.ip_entry.set_text(self.config.get("bridge_ip", ""))
        ip_box.pack_start(self.ip_entry, True, True, 0)
        box_conexion.pack_start(ip_box, False, False, 0)
        
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
        
        # Configuración de actualización
        config_frame = Gtk.Frame(label="⚙️ Configuración")
        config_frame.set_margin_top(5)
        config_frame.set_margin_bottom(5)
        config_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        config_box.set_margin_top(10)
        config_box.set_margin_bottom(10)
        config_box.set_margin_start(10)
        config_box.set_margin_end(10)
        
        config_box.pack_start(Gtk.Label(label="Actualizar sensores cada:"), False, False, 0)
        
        self.update_spin = Gtk.SpinButton()
        self.update_spin.set_range(1, 60)
        self.update_spin.set_value(self.update_interval / 60)
        self.update_spin.set_digits(0)
        self.update_spin.set_increments(1, 5)
        self.update_spin.connect("value-changed", self.on_update_interval_changed)
        config_box.pack_start(self.update_spin, False, False, 0)
        
        config_box.pack_start(Gtk.Label(label="minutos"), False, False, 0)
        
        config_frame.add(config_box)
        self.sidebar.pack_start(config_frame, False, False, 0)
        
        # Lista de habitaciones
        self.scroll_habitaciones = Gtk.ScrolledWindow()
        self.scroll_habitaciones.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_habitaciones.set_min_content_height(250)
        
        self.lista_habitaciones = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.lista_habitaciones.set_margin_top(10)
        self.lista_habitaciones.set_margin_bottom(10)
        self.lista_habitaciones.set_margin_start(10)
        self.lista_habitaciones.set_margin_end(10)
        
        self.scroll_habitaciones.add(self.lista_habitaciones)
        
        label_habitaciones = Gtk.Label()
        label_habitaciones.set_markup("<span weight='bold'>🏠 Habitaciones</span>")
        label_habitaciones.set_margin_bottom(10)
        self.sidebar.pack_start(label_habitaciones, False, False, 0)
        self.sidebar.pack_start(self.scroll_habitaciones, True, True, 0)
        
        # Panel de sensores
        self.sensores_frame = Gtk.Frame(label="🌡️ Sensores de Temperatura")
        self.sensores_frame.set_margin_top(10)
        self.sensores_frame.set_margin_bottom(10)
        
        self.sensores_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.sensores_box.set_margin_top(10)
        self.sensores_box.set_margin_bottom(10)
        self.sensores_box.set_margin_start(10)
        self.sensores_box.set_margin_end(10)
        
        self.sensores_scroll = Gtk.ScrolledWindow()
        self.sensores_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.sensores_scroll.set_min_content_height(150)
        
        self.sensores_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.sensores_container.set_margin_top(5)
        self.sensores_container.set_margin_bottom(5)
        
        self.sensores_scroll.add(self.sensores_container)
        self.sensores_box.pack_start(self.sensores_scroll, True, True, 0)
        self.sensores_frame.add(self.sensores_box)
        
        self.sidebar.pack_start(self.sensores_frame, False, False, 0)
        
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
        self.scroll_luces.set_min_content_height(600)
        
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
    
    def on_conectar_clicked(self, widget):
        """Maneja el click en el botón conectar"""
        ip = self.ip_entry.get_text().strip()
        
        if not ip:
            self.label_estado.set_markup("<span foreground='red'>❌ Error: Ingresa la IP del puente</span>")
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
        """Registra la aplicación en el puente Hue"""
        try:
            app_name = self.config.get("app_name", "hue_controller_linux")
            url = f"https://{self.bridge_ip}/api"
            data = {"devicetype": app_name}
            
            response = requests.post(url, json=data, verify=False, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'success' in result[0]:
                    self.api_key = result[0]['success']['username']
                    self.headers = {"hue-application-key": self.api_key, "Content-Type": "application/json"}
                    
                    self.config["api_key"] = self.api_key
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
                    if nuevo_estado:
                        self.sliders_luces[luz['id']].set_value(luz.get('brightness', 0))
                        self.sliders_luces[luz['id']].set_sensitive(True)
                    else:
                        self.sliders_luces[luz['id']].set_value(0)
                        self.sliders_luces[luz['id']].set_sensitive(False)
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
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        card.get_style_context().add_class("sensor-card")
        card.set_size_request(160, 100)
        
        ubicacion_texto = sensor_data['ubicacion'] if sensor_data['ubicacion'] != 'Sin ubicación' else 'Ubicación desconocida'
        ubicacion = Gtk.Label()
        ubicacion.set_markup(f"<span weight='bold' size='large'>📍 {ubicacion_texto}</span>")
        ubicacion.get_style_context().add_class("sensor-ubicacion")
        
        temp = Gtk.Label()
        temp.set_markup(f"<span size='x-large' weight='bold'>{sensor_data['temperature']:.1f}°C</span>")
        temp.get_style_context().add_class("sensor-temperatura")
        
        last_up = Gtk.Label()
        last_up.set_markup(f"<span size='x-small'>{sensor_data['last_updated'].strftime('%H:%M:%S')}</span>")
        last_up.get_style_context().add_class("sensor-updated")
        
        card.pack_start(ubicacion, False, False, 0)
        card.pack_start(temp, True, True, 0)
        card.pack_start(last_up, False, False, 0)
        
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
                    for device_id, device in self.devices.items():
                        if device.get('service_id') == light_id:
                            device['on'] = item.get('on', {}).get('on', False)
                            device['brightness'] = item.get('dimming', {}).get('brightness', 0)
                            
                            GLib.idle_add(self.actualizar_interfaz_luces)
        except Exception as e:
            print(f"Error actualizando estado luces: {e}")
    
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
                    self.switches_habitacion[self.habitacion_actual].set_active(alguna_encendida)
    
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
        slider.set_hexpand(True)
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
        try:
            switch.handler_block_by_func(self.on_luz_switch_toggled)
            
            nuevo_estado = switch.get_active()
            self.controlar_luz(luz, nuevo_estado)
            luz['on'] = nuevo_estado
            
            if luz['id'] in self.sliders_luces:
                if nuevo_estado:
                    self.sliders_luces[luz['id']].set_value(luz.get('brightness', 0))
                    self.sliders_luces[luz['id']].set_sensitive(True)
                else:
                    self.sliders_luces[luz['id']].set_value(0)
                    self.sliders_luces[luz['id']].set_sensitive(False)
            
            if self.habitacion_actual and self.habitacion_actual in self.rooms:
                room = self.rooms.get(self.habitacion_actual, {})
                luces_room = []
                for child in room.get('children', []):
                    if child.get('rid') in self.devices:
                        luces_room.append(self.devices[child.get('rid')])
                
                alguna_encendida = any(l.get('on', False) for l in luces_room)
                if self.habitacion_actual in self.switches_habitacion:
                    habitacion_switch = self.switches_habitacion[self.habitacion_actual]
                    habitacion_switch.handler_block_by_func(self.on_habitacion_switch_toggled)
                    habitacion_switch.set_active(alguna_encendida)
                    habitacion_switch.handler_unblock_by_func(self.on_habitacion_switch_toggled)
            
        except Exception as e:
            self.mostrar_error(f"Error al cambiar estado: {e}")
            switch.set_active(not nuevo_estado)
        finally:
            switch.handler_unblock_by_func(self.on_luz_switch_toggled)
    
    def on_brillo_changed(self, widget, luz):
        """Cambia el brillo de una luz"""
        try:
            porcentaje = int(widget.get_value())
            self.cambiar_brillo(luz, porcentaje)
            luz['brightness'] = porcentaje
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
    app = AppHueMejorada()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
