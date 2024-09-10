from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import json
from tools.camara import CameraController

class CalibrarScreen(Screen):
    current_time = StringProperty()
    camera_controller = None
    dropdown = None  # Dropdown para seleccionar las placas
    selected_tag_location = ListProperty([0.0, 0.0, 0.0])  # Coordenadas actuales de la placa seleccionada
    new_location = ListProperty([0.0, 0.0, 0.0])  # Nuevas coordenadas para la placa seleccionada

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)  # Actualiza el tiempo cada segundo

        # Iniciar cámara con controlador separado
        self.camera_controller = CameraController(camera_id=0)
        self.camera_controller.start_camera(self.ids.camera_image)

        # Configura el menú desplegable
        self.dropdown = DropDown()
        self.data = {}  # Variable para cargar los datos del JSON
        self.load_dropdown_items()  # Carga los datos del JSON para el dropdown

    def update_time(self, *args):
        from datetime import datetime
        self.current_time = datetime.now().strftime("%H:%M:%S")

    def on_stop(self):
        """Libera los recursos de la cámara al detener la aplicación"""
        self.camera_controller.stop_camera()

    def go_back(self):
        self.manager.current = 'inicio'

    def show_dropdown(self):
        """Abre el dropdown cuando se hace clic en el botón"""
        self.dropdown.open(self.ids.dropdown_button)

    def create_dropdown_items(self, items):
        """Crea las opciones del dropdown con los elementos del JSON"""
        self.dropdown.clear_widgets()
        for item in items:
            btn = Button(text=str(item), size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_dropdown_item(btn.text))
            self.dropdown.add_widget(btn)

    def select_dropdown_item(self, value):
        """Acción que se realiza al seleccionar un ítem del dropdown"""
        print(f"Selección del dropdown: {value}")
        self.ids.dropdown_button.text = value
        self.dropdown.dismiss()

        # Busca la ubicación en el JSON
        tag_data = next((tag for tag in self.data['tags'] if str(tag['tag']) == value), None)
        if tag_data:
            location = tag_data.get('location', [0.0, 0.0, 0.0])  # Asegúrate de que tiene 3 valores
            if len(location) == 2:  # Si solo tiene x e y
                location.append(0.0)  # Añade z = 0.0 si falta
            self.selected_tag_location = location
            self.new_location = location.copy()  # Copia los valores para permitir modificación sin afectar los originales
            print(f"Ubicación seleccionada: {self.selected_tag_location}")  # Debug

    def load_dropdown_items(self):
        """Carga los ítems del dropdown desde un archivo JSON"""
        try:
            with open('./app/config/coordinates_10.json', 'r') as file:
                self.data = json.load(file)
                tags = [str(tag['tag']) for tag in self.data.get('tags', [])]
                self.create_dropdown_items(tags)
        except FileNotFoundError:
            print("Archivo JSON no encontrado.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")

    # Métodos para mover los ejes
    def move_x_positive(self):
        self.new_location[0] += 0.5
        print("Mover eje X positivo:", self.new_location[0])  # Debug para ver el valor actualizado

    def move_x_negative(self):
        self.new_location[0] -= 0.5
        print("Mover eje X negativo:", self.new_location[0])

    def move_y_positive(self):
        self.new_location[1] += 0.5
        print("Mover eje Y positivo:", self.new_location[1])

    def move_y_negative(self):
        self.new_location[1] -= 0.5
        print("Mover eje Y negativo:", self.new_location[1])

    def move_z_positive(self):
        self.new_location[2] += 0.5
        print("Mover eje Z positivo:", self.new_location[2])

    def move_z_negative(self):
        self.new_location[2] -= 0.5
        print("Mover eje Z negativo:", self.new_location[2])

    def save_settings(self):
        print(f"Guardando la nueva ubicación: {self.new_location}")
        
        # Busca el tag seleccionado en los datos
        for tag in self.data['tags']:
            if str(tag['tag']) == self.ids.dropdown_button.text:
                tag['location'] = self.new_location  # Actualiza con los nuevos valores
                break

        # Guarda los datos actualizados en el archivo JSON
        with open('./app/config/coordinates_10.json', 'w') as file:
            json.dump(self.data, file, indent=4)
        
        print("Configuración guardada.")
