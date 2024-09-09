from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import cv2
import json

class CalibrarScreen(Screen):
    current_time = StringProperty()
    camera_id = 0  # Índice de la cámara, generalmente 0 para la cámara principal
    capture = None
    dropdown = None  # Dropdown para seleccionar las placas

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)  # Actualiza el tiempo cada segundo
        self.start_camera()

        # Configura el menú desplegable
        self.dropdown = DropDown()
        self.load_dropdown_items()  # Carga los datos del JSON para el dropdown

    def update_time(self, *args):
        from datetime import datetime
        self.current_time = datetime.now().strftime("%H:%M:%S")

    def start_camera(self):
        """Inicia la captura de video desde la cámara USB"""
        self.capture = cv2.VideoCapture(self.camera_id)
        if not self.capture.isOpened():
            # Si no se puede abrir la cámara, carga la imagen predeterminada
            self.ids.camera_image.source = './app/resources/img/cam.png'
            return
        
        # Configura la actualización del frame en un intervalo regular
        Clock.schedule_interval(self.update_frame, 1.0 / 30)  # Actualiza a 30 FPS

    def update_frame(self, *args):
        """Actualiza el frame de la cámara y lo muestra en la pantalla"""
        ret, frame = self.capture.read()
        if ret:
            # Convierte el frame de BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Gira verticalmente la imagen
            frame = frame[::-1]
            # Convierte la imagen a una textura de Kivy
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            # Actualiza la textura en el Image de Kivy
            self.ids.camera_image.texture = texture
        else:
            # Si no se puede capturar, muestra la imagen predeterminada
            self.ids.camera_image.source = './app/resources/img/cam.png'

    def on_stop(self):
        """Libera los recursos de la cámara al detener la aplicación"""
        if self.capture:
            self.capture.release()

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

    def load_dropdown_items(self):
        """Carga los ítems del dropdown desde un archivo JSON"""
        try:
            with open('./Ci24/devices/config/coordinates_10.json', 'r') as file:
                data = json.load(file)
                tags = [str(tag['tag']) for tag in data.get('tags', [])]
                self.create_dropdown_items(tags)
        except FileNotFoundError:
            print("Archivo JSON no encontrado.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")

    # Métodos para mover los ejes
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
