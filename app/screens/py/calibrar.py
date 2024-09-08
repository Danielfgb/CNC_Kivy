from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import json
import requests

class CalibrarScreen(Screen):
    current_time = StringProperty()
    stream_url = "http://localhost:8080/feed.mjpeg"  # URL del stream de la cámara

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)  # Actualiza el tiempo cada segundo
        self.check_camera_stream()

        # Configura el menú desplegable
        self.dropdown = DropDown()
        self.load_dropdown_items()  # Carga los datos del JSON para el dropdown

    def update_time(self, *args):
        from datetime import datetime
        self.current_time = datetime.now().strftime("%H:%M:%S")

    def go_back(self):
        self.manager.current = 'inicio'

    def check_camera_stream(self):
        """Verifica si el stream de la cámara está disponible"""
        try:
            response = requests.get(self.stream_url, stream=True, timeout=5)
            if response.status_code == 200:
                # Si el stream está disponible, muestra la URL
                self.ids.camera_image.source = self.stream_url
            else:
                # Si el stream no está disponible, usa la imagen predeterminada
                self.ids.camera_image.source = './app/resources/img/cam.png'
        except requests.exceptions.RequestException:
            # Si ocurre un error, también muestra la imagen predeterminada
            self.ids.camera_image.source = './app/resources/img/cam.png'

    # Métodos existentes para mover los ejes y otras funcionalidades
    def move_x_positive(self):
        print("Mover eje X positivo")

    def move_x_negative(self):
        print("Mover eje X negativo")
    
    def move_y_positive(self):
        print("Mover eje Y positivo")
    
    def move_y_negative(self):
        print("Mover eje Y negativo")

    def move_z_positive(self):
        print("Mover eje Z positivo")
    
    def move_z_negative(self):
        print("Mover eje Z negativo")

    def save_settings(self):
        print("Guardar configuración")

    def show_dropdown(self):
        self.dropdown.open(self.ids.dropdown_button)

    def create_dropdown_items(self, items):
        self.dropdown.clear_widgets()
        for item in items:
            btn = Button(text=str(item), size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_dropdown_item(btn.text))
            self.dropdown.add_widget(btn)

    def select_dropdown_item(self, value):
        print(f"Selección del dropdown: {value}")

    def load_dropdown_items(self):
        try:
            with open('./app/resources/data/coordinates_10.json', 'r') as file:
                data = json.load(file)
                tags = [str(tag['tag']) for tag in data.get('tags', [])]
                self.create_dropdown_items(tags)
        except FileNotFoundError:
            print("Archivo JSON no encontrado.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")
