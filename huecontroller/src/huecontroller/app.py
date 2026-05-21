"""
Philips Hue Controller - Aplicación para controlar luces Philips Hue
"""

import sys
import os

# Asegurar que podemos importar toga
try:
    import toga
    from toga.style import Pack
    from toga.style.pack import COLUMN, ROW
except ImportError as e:
    print(f"Error importando toga: {e}")
    print("Instala toga con: pip install toga==0.4.8")
    sys.exit(1)

from phue import Bridge
import threading
import json

class HueController(toga.App):
    def startup(self):
        """Configurar la aplicación al iniciar"""
        # Variables
        self.bridge = None
        self.grupos = {}
        self.luces = {}
        self.escenas_por_grupo = {}
        self.luces_info = {}
        self.switches_luces = {}
        self.sliders_luces = {}
        
        # Crear la ventana principal
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.size = (1080, 800)
        
        # Contenedor principal
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Título
        title = toga.Label(
            "🏠 Philips Hue Controller",
            style=Pack(padding=(0, 0, 10, 0), font_size=20, font_weight="bold")
        )
        main_box.add(title)
        
        # Panel de conexión
        connect_box = toga.Box(style=Pack(direction=COLUMN, padding=5, background_color="#f0f0f0"))
        
        # IP Entry
        ip_box = toga.Box(style=Pack(direction=ROW, padding=5))
        ip_box.add(toga.Label("IP del puente:", style=Pack(width=100)))
        self.ip_input = toga.TextInput(placeholder="192.168.68.54", style=Pack(flex=1))
        
        # Cargar IP guardada
        self.config_path = os.path.expanduser("~/.hue_controller_config.json")
        self.cargar_configuracion()
        
        ip_box.add(self.ip_input)
        connect_box.add(ip_box)
        
        # Botón conectar
        self.btn_conectar = toga.Button(
            "🔌 Conectar al puente",
            on_press=self.on_conectar,
            style=Pack(padding=5, background_color="#4CAF50", color="white")
        )
        connect_box.add(self.btn_conectar)
        
        # Estado de conexión
        self.label_estado = toga.Label(
            "⚪ Estado: No conectado",
            style=Pack(padding=5, color="#666")
        )
        connect_box.add(self.label_estado)
        
        main_box.add(connect_box)
        
        # Contenedor para habitaciones
        self.habitaciones_scroll = toga.ScrollContainer(style=Pack(flex=1, padding=5))
        self.habitaciones_box = toga.Box(style=Pack(direction=COLUMN, spacing=5))
        self.habitaciones_scroll.content = self.habitaciones_box
        
        # Panel de habitaciones
        habitaciones_label = toga.Label(
            "🏠 Habitaciones y Zonas",
            style=Pack(padding=(10, 0, 5, 0), font_weight="bold")
        )
        main_box.add(habitaciones_label)
        main_box.add(self.habitaciones_scroll)
        
        # Panel de escenas (se mostrará cuando se seleccione una habitación)
        self.escenas_frame = toga.Box(
            style=Pack(direction=COLUMN, padding=10, border=1, border_color="#3498db", 
                       border_radius=8, margin=5)
        )
        
        self.escenas_titulo = toga.Label(
            "ESCENAS",
            style=Pack(padding=(0, 0, 10, 0), font_weight="bold", color="#2980b9")
        )
        self.escenas_frame.add(self.escenas_titulo)
        
        self.escenas_scroll = toga.ScrollContainer(style=Pack(height=120))
        self.escenas_container = toga.Box(style=Pack(direction=ROW, spacing=10))
        self.escenas_scroll.content = self.escenas_container
        self.escenas_frame.add(self.escenas_scroll)
        
        main_box.add(self.escenas_frame)
        
        # Panel de luces
        luces_label = toga.Label(
            "💡 Luces",
            style=Pack(padding=(10, 0, 5, 0), font_weight="bold")
        )
        main_box.add(luces_label)
        
        self.luces_scroll = toga.ScrollContainer(style=Pack(flex=1, padding=5))
        self.luces_container = toga.Box(style=Pack(direction=COLUMN, spacing=5))
        self.luces_scroll.content = self.luces_container
        main_box.add(self.luces_scroll)
        
        # Spinner de carga
        self.spinner = toga.ActivityIndicator(style=Pack(padding=10))
        main_box.add(self.spinner)
        
        # Variables
        self.habitacion_actual = None
        self.botones_habitacion = {}
        self.switches_habitacion = {}
        
        # Ocultar panel de escenas inicialmente
        self.escenas_frame.style.visibility = "hidden"
        
        # Mostrar la ventana
        self.main_window.content = main_box
        self.main_window.show()
    
    def cargar_configuracion(self):
        """Carga la configuración guardada"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.ip_input.value = config.get("bridge_ip", "192.168.68.54")
        except Exception as e:
            print(f"Error cargando configuración: {e}")
    
    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        try:
            config = {"bridge_ip": self.ip_input.value}
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    async def on_conectar(self, widget):
        """Maneja el click en el botón conectar"""
        ip = self.ip_input.value.strip()
        if not ip:
            self.label_estado.text = "❌ Error: Ingresa la IP del puente"
            self.label_estado.style.color = "red"
            return
        
        self.guardar_configuracion()
        
        self.label_estado.text = "🔄 Conectando..."
        self.label_estado.style.color = "orange"
        self.btn_conectar.enabled = False
        self.spinner.start()
        
        # Conectar en hilo separado
        threading.Thread(target=self.conectar_al_bridge, args=(ip,), daemon=True).start()
    
    def conectar_al_bridge(self, ip):
        """Conecta al bridge en un hilo separado"""
        try:
            bridge = Bridge(ip)
            bridge.get_api()
            self.bridge = bridge
            self.main_window.loop.call_soon_threadsafe(self.conexion_exitosa)
        except Exception as e:
            self.main_window.loop.call_soon_threadsafe(self.conexion_fallida, str(e))
    
    def conexion_exitosa(self):
        """Maneja la conexión exitosa"""
        self.label_estado.text = "✅ Conectado al puente"
        self.label_estado.style.color = "green"
        self.btn_conectar.enabled = False
        self.spinner.stop()
        
        # Cargar grupos, luces y escenas
        threading.Thread(target=self.cargar_grupos_luces_y_escenas, daemon=True).start()
    
    def conexion_fallida(self, error_msg):
        """Maneja errores de conexión"""
        self.label_estado.text = f"❌ Error: {error_msg}"
        self.label_estado.style.color = "red"
        self.btn_conectar.enabled = True
        self.spinner.stop()
    
    def cargar_grupos_luces_y_escenas(self):
        """Carga todos los grupos y sus luces"""
        # Esta es una versión simplificada - implementa la lógica completa aquí
        self.main_window.loop.call_soon_threadsafe(
            lambda: self.mostrar_info("Info", "Conectado al puente. Implementa la carga de grupos aquí.")
        )
    
    def mostrar_error(self, mensaje):
        """Muestra un diálogo de error"""
        self.main_window.error_dialog("Error", mensaje)
    
    def mostrar_info(self, titulo, mensaje):
        """Muestra un diálogo de información"""
        self.main_window.info_dialog(titulo, mensaje)


def main():
    """Punto de entrada principal"""
    return HueController()


if __name__ == "__main__":
    app = main()
    app.main_loop()

