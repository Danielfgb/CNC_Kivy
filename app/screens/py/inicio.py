from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty
from .login_popup import LoginPopup

class InicioScreen(Screen):
    current_time = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_time()
        Clock.schedule_interval(self.update_time, 1)  

    def update_time(self, *args):
        from datetime import datetime
        self.current_time = datetime.now().strftime("%H:%M:%S")

    def show_login_popup(self):
        login_popup = LoginPopup()
        login_popup.show()
