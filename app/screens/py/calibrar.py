from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog

from kivymd.uix.button import MDFlatButton 
from kivy.uix.boxlayout import BoxLayout

import json
import shutil

from tools.camara import CameraController
from tools.cnc import CNCController
from tools.GPIO import GPIOController

class DistanceDialogContent(BoxLayout):
    pass


class CalibrarScreen(Screen):
    current_time = StringProperty()
    camera_controller = None
    gpio_controller = None
    selected_tag_location = ListProperty([0.0, 0.0, 0.0])  # Coordenadas del tag seleccionado
    new_location = ListProperty([0.0, 0.0, 0.0])  # Nuevas coordenadas para el movimiento manual

    # Límites de los ejes
    MAX_X = 200.0
    MAX_Y = 200.0
    MIN_Z = -85.0  # Eje Z invertido: home es 0 y el máximo es -85
    MIN_XY = 0.0  # El mínimo para X e Y es 0

    travel_distance_x_y = NumericProperty(20)  # Valor inicial para X e Y
    travel_distance_z = NumericProperty(10)    # Valor para Z

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)

        # Iniciar cámara con controlador separado
        self.camera_controller = CameraController(camera_id=0)
        self.camera_controller.start_camera(self.ids.camera_image)

        # Cargar los datos del JSON y configurar el menú
        self.data = {}  # Variable para cargar los datos del JSON
        self.load_dropdown_items()

        # Conectar con el controlador CNC
        self.cnc = CNCController(['/dev/ttyUSB0', '/dev/ttyUSB1'])

        self.gpio_controller = GPIOController()
        self.controladora = True

    def modify_travel_distance(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Modificar Recorrido",
                type="custom",
                content_cls=DistanceDialogContent(),
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        on_release=lambda *args: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="OK",
                        on_release=self.update_travel_distance
                    ),
                ],
            )
        self.dialog.open()

    def update_travel_distance(self, *args):
        try:
            # Obtener el valor ingresado en el campo de texto del diálogo
            x_y_value = float(self.dialog.content_cls.ids.x_y_field.text)

            # Validar que los valores estén entre 0 y 200
            if 0 <= x_y_value <= 200:
                self.travel_distance_x_y = x_y_value
                print(f"Nuevo valor de recorrido para X e Y: {self.travel_distance_x_y} mm")
                self.travel_distance_z = 10  # Mantener Z fijo en 10 mm
            else:
                print("El valor de recorrido debe estar entre 0 y 200 mm")
        except ValueError:
            print("Valor inválido, por favor ingrese un número válido")

        # Cerrar el diálogo
        self.dialog.dismiss()
        
    def stop_all_movement(self):
        """Detiene todo el movimiento de la CNC"""
        self.cnc.stop_all() 

    def toggle_zoom(self):
        """Alterna el estado de zoom de la cámara."""
        self.camera_controller.toggle_zoom()
        print("zoom")

    def on_enter(self):
        """Al entrar en la pantalla de calibración, ir a home."""
        if self.controladora:  # Verificar si la variable controladora es True
            self.gpio_controller.activate_cnc()
        self.cnc.connect()
        self.cnc.go_home()

    def update_time(self, *args):
        from datetime import datetime
        self.current_time = datetime.now().strftime("%H:%M:%S")

    def on_stop(self):
        """Libera los recursos de la cámara al detener la aplicación."""
        self.camera_controller.stop_camera()
        self.gpio_controller.cleanup()

    def go_back(self):
        self.manager.current = 'inicio'
        self.gpio_controller.deactivate_cnc()

    def show_menu(self, caller):
        """Abre el menú desplegable con los números de tags."""
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Placa {tag['tag']}",
                "height": dp(56),
                "on_release": lambda x=f"Placa {tag['tag']}": self.select_dropdown_item(x)
            } for tag in self.data.get('tags', [])
        ]
        
        self.menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=3,
            max_height =dp(336)
        )
        self.menu.open()

    def select_dropdown_item(self, value):
        """Acción que se realiza al seleccionar un ítem del menú."""
        tag_number = value.split(" ")[1]  # Obtener solo el número del tag
        self.ids.dropdown_button.text = value
        self.menu.dismiss()

        # Busca la ubicación en el JSON
        tag_data = next((tag for tag in self.data['tags'] if str(tag['tag']) == tag_number), None)
        if tag_data and 'location' in tag_data:
            location = tag_data['location']
            self.selected_tag_location = location
            self.new_location = location.copy()
            print(f"Ubicación seleccionada: {self.selected_tag_location}")
            self.move_to_tag()
        else:
            print(f"No se encontró la ubicación para el tag: {tag_number}")

    def load_dropdown_items(self):
        """Carga los ítems del dropdown desde un archivo JSON."""
        try:
            with open('./app/config/coordinates_10.json', 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print("Archivo JSON no encontrado.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")

    def move_to_tag(self):
        """Envía las coordenadas del tag seleccionado al CNC para que se mueva a dicha posición."""
        if self.selected_tag_location:
            x, y, z = self.selected_tag_location
            self.cnc.move_to(x=x, y=y, z=0)  # Mover siempre a Z=0
            self.new_location = [x, y, 0]
            print(f"Moviendo a la posición del tag: X={x}, Y={y}, Z=0")
        else:
            print("No se ha seleccionado un tag o las coordenadas están incompletas.")

    def save_settings(self):
        print(f"Guardando la nueva ubicación: {self.new_location}")

        # Busca el tag seleccionado en los datos
        for tag in self.data['tags']:
            if str(tag['tag']) == self.ids.dropdown_button.text.split(" ")[1]:
                tag['location'] = self.new_location
                break

        # Guarda los datos actualizados en el archivo JSON
        with open('./app/config/coordinates_10.json', 'w') as file:
            json.dump(self.data, file, indent=4)
        
        print("Configuración guardada.")

    def go_home(self):
        self.cnc.go_home()
        self.new_location = [0.0, 0.0, 0.0]

    def reset_coordinates(self):
        """Restablece las coordenadas copiando el contenido del archivo JSON backup."""
        backup_file = './app/config/coordinates_10 copy.json'
        target_file = './app/config/coordinates_10.json'
        try:
            shutil.copyfile(backup_file, target_file)
            print(f"Coordenadas restablecidas desde {backup_file}")
        except Exception as e:
            print(f"Error al restablecer coordenadas: {e}")

    # Métodos para mover los ejes manualmente
def move_x_positive(self):
    if self.new_location[0] + self.travel_distance_x_y <= self.MAX_X:
        self.new_location[0] += self.travel_distance_x_y
    else:
        self.new_location[0] = self.MAX_X
    self.cnc.move_to(x=self.new_location[0])
    print(f"Moviendo eje X positivo a: {self.new_location[0]}")

def move_x_negative(self):
    if self.new_location[0] - self.travel_distance_x_y >= self.MIN_XY:
        self.new_location[0] -= self.travel_distance_x_y
    else:
        self.new_location[0] = self.MIN_XY
    self.cnc.move_to(x=self.new_location[0])
    print(f"Moviendo eje X negativo a: {self.new_location[0]}")

def move_y_positive(self):
    if self.new_location[1] + self.travel_distance_x_y <= self.MAX_Y:
        self.new_location[1] += self.travel_distance_x_y
    else:
        self.new_location[1] = self.MAX_Y
    self.cnc.move_to(y=self.new_location[1])
    print(f"Moviendo eje Y positivo a: {self.new_location[1]}")

def move_y_negative(self):
    if self.new_location[1] - self.travel_distance_x_y >= self.MIN_XY:
        self.new_location[1] -= self.travel_distance_x_y
    else:
        self.new_location[1] = self.MIN_XY
    self.cnc.move_to(y=self.new_location[1])
    print(f"Moviendo eje Y negativo a: {self.new_location[1]}")
