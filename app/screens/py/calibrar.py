from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

class CalibrarScreen(Screen):
    current_time = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)  # Actualiza el tiempo cada segundo

        # Configura el menú desplegable
        self.dropdown = DropDown()
        self.create_dropdown_items([40, 50])  # Añade los números iniciales al dropdown

    def update_time(self, *args):
        from datetime import datetime
        self.current_time = datetime.now().strftime("%H:%M:%S")
    
    def go_back(self):
        self.manager.current = 'inicio'
    
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

