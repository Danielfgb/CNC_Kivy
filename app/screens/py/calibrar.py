from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import json
from tools.camara import CameraController
from tools.cnc import CNCController  # Importa CNCController desde app/tools/cnc.py

class CalibrarScreen(Screen):
    current_time = StringProperty()
    camera_controller = None
    dropdown = None
    selected_tag_location = ListProperty([0.0, 0.0, 0.0])  # Coordenadas del tag seleccionado
    new_location = ListProperty([0.0, 0.0, 0.0])  # Nuevas coordenadas para el movimiento manual

    # Límites de los ejes
    MAX_X = 200.0
    MAX_Y = 200.0
    MIN_Z = -85.0  # Eje Z invertido: home es 0 y el máximo es -85
    MIN_XY = 0.0  # El mínimo para X e Y es 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)

        # Iniciar cámara con controlador separado
        self.camera_controller = CameraController(camera_id=0)
        self.camera_controller.start_camera(self.ids.camera_image)

        # Configura el menú desplegable
        self.dropdown = DropDown()
        self.data = {}  # Variable para cargar los datos del JSON
        self.load_dropdown_items()

        # Conectar con el controlador CNC
        self.cnc = CNCController(['/dev/ttyUSB0', '/dev/ttyUSB1'])

    def on_enter(self):
        """Al entrar en la pantalla de calibración, ir a home."""
        self.cnc.connect()
        self.cnc.go_home()  # Ir a home al entrar a la ventana

    def update_time(self, *args):
        from datetime import datetime
        self.current_time = datetime.now().strftime("%H:%M:%S")

    def on_stop(self):
        """Libera los recursos de la cámara al detener la aplicación."""
        self.camera_controller.stop_camera()

    def go_back(self):
        self.manager.current = 'inicio'

    def show_dropdown(self):
        """Abre el dropdown cuando se hace clic en el botón."""
        self.dropdown.open(self.ids.dropdown_button)

    def create_dropdown_items(self, items):
        """Crea las opciones del dropdown con los elementos del JSON."""
        self.dropdown.clear_widgets()
        for item in items:
            btn = Button(text=str(item), size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_dropdown_item(btn.text))
            self.dropdown.add_widget(btn)

    def select_dropdown_item(self, value):
        """Acción que se realiza al seleccionar un ítem del dropdown."""
        print(f"Selección del dropdown: {value}")
        self.ids.dropdown_button.text = value
        self.dropdown.dismiss()

        # Busca la ubicación en el JSON
        tag_data = next((tag for tag in self.data['tags'] if str(tag['tag']) == value), None)
        if tag_data:
            location = tag_data.get('location', [0.0, 0.0, 0.0])
            self.selected_tag_location = location
            self.new_location = location.copy()
            print(f"Ubicación seleccionada: {self.selected_tag_location}")

            # Mover a la posición del tag seleccionado
            self.move_to_tag()

    def load_dropdown_items(self):
        """Carga los ítems del dropdown desde un archivo JSON."""
        try:
            with open('./app/config/coordinates_10.json', 'r') as file:
                self.data = json.load(file)
                tags = [str(tag['tag']) for tag in self.data.get('tags', [])]
                self.create_dropdown_items(tags)
        except FileNotFoundError:
            print("Archivo JSON no encontrado.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")

    # Métodos para mover los ejes manualmente
    def move_x_positive(self):
        if self.new_location[0] + 20 <= self.MAX_X:
            self.new_location[0] += 20
        else:
            self.new_location[0] = self.MAX_X
        self.cnc.move_to(x=self.new_location[0])
        print(f"Moviendo eje X positivo a: {self.new_location[0]}")

    def move_x_negative(self):
        if self.new_location[0] - 20 >= self.MIN_XY:
            self.new_location[0] -= 20
        else:
            self.new_location[0] = self.MIN_XY
        self.cnc.move_to(x=self.new_location[0])
        print(f"Moviendo eje X negativo a: {self.new_location[0]}")

    def move_y_positive(self):
        if self.new_location[1] + 20 <= self.MAX_Y:
            self.new_location[1] += 20
        else:
            self.new_location[1] = self.MAX_Y
        self.cnc.move_to(y=self.new_location[1])
        print(f"Moviendo eje Y positivo a: {self.new_location[1]}")

    def move_y_negative(self):
        if self.new_location[1] - 20 >= self.MIN_XY:
            self.new_location[1] -= 20
        else:
            self.new_location[1] = self.MIN_XY
        self.cnc.move_to(y=self.new_location[1])
        print(f"Moviendo eje Y negativo a: {self.new_location[1]}")

    def move_z_positive(self):
        if self.new_location[2] + 20 <= 0:  # El límite superior es 0
            self.new_location[2] += 20
        else:
            self.new_location[2] = 0
        self.cnc.move_to(z=self.new_location[2])
        print(f"Moviendo eje Z positivo a: {self.new_location[2]}")

    def move_z_negative(self):
        if self.new_location[2] - 20 >= self.MIN_Z:
            self.new_location[2] -= 20
        else:
            self.new_location[2] = self.MIN_Z
        self.cnc.move_to(z=self.new_location[2])
        print(f"Moviendo eje Z negativo a: {self.new_location[2]}")

    def move_to_tag(self):
        """Envía las coordenadas del tag seleccionado al CNC para que se mueva a dicha posición."""
        if self.selected_tag_location:
            x, y, z = self.selected_tag_location
            self.cnc.move_to(x=x, y=y, z=z)
            print(f"Moviendo a la posición del tag: X={x}, Y={y}, Z={z}")
        else:
            print("No se ha seleccionado un tag o las coordenadas están incompletas.")

    def save_settings(self):
        print(f"Guardando la nueva ubicación: {self.new_location}")

        # Busca el tag seleccionado en los datos
        for tag in self.data['tags']:
            if str(tag['tag']) == self.ids.dropdown_button.text:
                tag['location'] = self.new_location
                break

        # Guarda los datos actualizados en el archivo JSON
        with open('./app/config/coordinates_10.json', 'w') as file:
            json.dump(self.data, file, indent=4)
        
        print("Configuración guardada.")

    def go_home(self):
        self.cnc.go_home()
