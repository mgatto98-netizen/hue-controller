# app_hue.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from phue import Bridge
import threading
import sys

# --- Clase Principal de la Aplicación ---
class AppHue(Gtk.Window):
    def __init__(self):
        super().__init__(title="Control Philips Hue para Linux")
        self.set_default_size(400, 400)
        self.set_border_width(15)

        # Variable para guardar el objeto del puente (bridge)
        self.bridge = None

        # --- Crear los elementos de la interfaz ---
        # Un grid para organizar los controles
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        self.add(grid)

        # --- Fila 1: IP del puente y Botón de conexión ---
        label_ip = Gtk.Label(label="IP del Puente:")
        grid.attach(label_ip, 0, 0, 1, 1)

        self.entry_ip = Gtk.Entry()
        self.entry_ip.set_placeholder_text("Ej: 192.168.1.100")
        grid.attach(self.entry_ip, 1, 0, 1, 1)

        self.btn_conectar = Gtk.Button(label="Conectar")
        self.btn_conectar.connect("clicked", self.on_conectar_clicked)
        grid.attach(self.btn_conectar, 2, 0, 1, 1)

        # --- Fila 2: Estado de conexión ---
        self.label_estado = Gtk.Label(label="Estado: No conectado")
        grid.attach(self.label_estado, 0, 1, 3, 1)

        # --- Fila 3 y siguientes: Lista de luces (se llenará después de conectar)---
        self.lista_luces_frame = Gtk.Frame(label="Luces encontradas")
        self.lista_luces_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.lista_luces_frame.add(self.lista_luces_box)
        grid.attach(self.lista_luces_frame, 0, 2, 3, 1)

        # Un 'spinner' para mostrar que estamos cargando
        self.spinner = Gtk.Spinner()
        grid.attach(self.spinner, 0, 3, 3, 1)

        self.show_all()

    # --- Función que se ejecuta al hacer clic en "Conectar" ---
    def on_conectar_clicked(self, widget):
        ip = self.entry_ip.get_text().strip()
        if not ip:
            self.label_estado.set_text("Estado: Por favor, ingresa la IP del puente.")
            return

        self.label_estado.set_text("Estado: Conectando...")
        self.btn_conectar.set_sensitive(False)
        self.spinner.start()

        # Conectar al puente puede tomar tiempo, así que usamos un hilo (thread)
        threading.Thread(target=self.conectar_al_bridge, args=(ip,), daemon=True).start()

    # --- Lógica de conexión (se ejecuta en un hilo separado)---
    def conectar_al_bridge(self, ip):
        try:
            # Intentamos conectar al puente
            bridge = Bridge(ip)
            # Este método lanza un error si no estamos autorizados
            bridge.get_api()
            # Si llegamos aquí, la conexión fue exitosa.
            # Nota: Si es la PRIMERA VEZ que te conectas desde este código, 
            # debes presionar el botón físico en el puente Hue y luego ejecutar 'bridge.connect()'.
            # Para simplificar, asumiremos que ya tienes un usuario registrado en el puente.
            # Si falla, la línea 'bridge.get_api()' lanzará una excepción.
            self.bridge = bridge

            # Actualizamos la UI desde el hilo principal
            GLib.idle_add(self.conexion_exitosa)
        except Exception as e:
            # En caso de error, lo mostramos en la UI
            GLib.idle_add(self.conexion_fallida, str(e))

    def conexion_exitosa(self):
        self.label_estado.set_text("Estado: Conectado y autorizado.")
        self.btn_conectar.set_sensitive(False)
        self.spinner.stop()
        self.spinner.hide()
        # Cargar la lista de luces
        self.cargar_lista_luces()
        return False # Necesario para que GLib.idle_add no se repita

    def conexion_fallida(self, error_msg):
        self.label_estado.set_text(f"Estado: Error - {error_msg}")
        self.btn_conectar.set_sensitive(True)
        self.spinner.stop()
        self.spinner.hide()
        return False

    # --- Obtiene las luces del puente y crea los controles en la UI ---
    def cargar_lista_luces(self):
        # Limpiar la caja de la lista de luces
        for child in self.lista_luces_box.get_children():
            self.lista_luces_box.remove(child)

        try:
            # 'get_light_objects' nos da una lista de objetos 'Light'
            luces = self.bridge.get_light_objects('name')
            if not luces:
                label = Gtk.Label(label="No se encontraron luces en el puente.")
                self.lista_luces_box.add(label)
            else:
                for nombre, luz in luces.items():
                    # Crear un frame para cada luz
                    frame_luz = Gtk.Frame(label=nombre)
                    box_luz = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    box_luz.set_margin_top(5)
                    box_luz.set_margin_bottom(5)
                    box_luz.set_margin_start(5)
                    box_luz.set_margin_end(5)
                    
                    # --- Control de Encendido/Apagado ---
                    btn_on_off = Gtk.Button()
                    # Estado inicial del botón
                    if luz.on:
                        btn_on_off.set_label("Apagar")
                    else:
                        btn_on_off.set_label("Encender")
                    # Conectar el evento, pasando la luz y el botón como argumentos
                    btn_on_off.connect("clicked", self.on_on_off_clicked, luz, btn_on_off)
                    
                    # --- Control de Brillo (slider) ---
                    # El valor de brillo va de 0 a 254
                    ajuste_brillo = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 254, 1)
                    ajuste_brillo.set_value(luz.bri if luz.on else 0) # Si está apagada, slider a 0
                    ajuste_brillo.set_digits(0) # Sin decimales
                    ajuste_brillo.set_hexpand(True)
                    ajuste_brillo.connect("value-changed", self.on_brillo_changed, luz)
                    
                    # Añadir controles al box de la luz
                    box_luz.pack_start(btn_on_off, False, False, 0)
                    box_luz.pack_start(ajuste_brillo, True, True, 0)
                    
                    # Guardar el slider dentro del frame_luz para actualizarlo después
                    frame_luz.ajuste_brillo = ajuste_brillo
                    frame_luz.add(box_luz)
                    self.lista_luces_box.add(frame_luz)
            
            self.lista_luces_box.show_all()
        except Exception as e:
            label_error = Gtk.Label(label=f"Error al cargar luces: {e}")
            self.lista_luces_box.add(label_error)
            self.lista_luces_box.show_all()

    # --- Callback para el botón de Encender/Apagar ---
    def on_on_off_clicked(self, widget, luz, btn_widget):
        try:
            if luz.on:
                # Apagar
                luz.on = False
                btn_widget.set_label("Encender")
                # Actualizar slider visualmente
                if hasattr(widget.get_parent().get_parent(), 'ajuste_brillo'):
                    widget.get_parent().get_parent().ajuste_brillo.set_value(0)
            else:
                # Encender
                luz.on = True
                btn_widget.set_label("Apagar")
                # Actualizar slider con el brillo actual de la luz
                if hasattr(widget.get_parent().get_parent(), 'ajuste_brillo'):
                    widget.get_parent().get_parent().ajuste_brillo.set_value(luz.bri)
        except Exception as e:
            print(f"Error: {e}")
            # Podrías mostrar un diálogo de error aquí

    # --- Callback para el control deslizante de brillo ---
    def on_brillo_changed(self, widget, luz):
        try:
            nuevo_brillo = int(widget.get_value())
            # La luz debe estar encendida para cambiar el brillo. 
            # Si está apagada, el comando no tendrá efecto o dará error.
            if luz.on:
                luz.brightness = nuevo_brillo
            else:
                # Opcional: si mueves el slider cuando está apagada, podrías encenderla.
                # Descomenta la siguiente línea si quieres ese comportamiento.
                # luz.on = True
                pass
        except Exception as e:
            print(f"Error al cambiar brillo: {e}")

# --- Punto de entrada de la aplicación ---
if __name__ == "__main__":
    app = AppHue()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()
    
