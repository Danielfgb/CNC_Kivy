import os
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from screens import InicioScreen, CalibrarScreen 
from kivy.core.window import Window 

class MainApp(MDApp): 
    def build(self):

# ROTACION DE PANTALLA PARA PRUEBAS CON MONITOR 
        Window.rotation = 270
        #Window.size = (1024,768)

        self.load_all_kv_files("./app/screens/kv")

        sm = ScreenManager()
        sm.add_widget(InicioScreen(name='inicio'))
        sm.add_widget(CalibrarScreen(name='calibrar'))
        return sm

    def load_all_kv_files(self, kv_dir):
        for kv_file in os.listdir(kv_dir):
            if kv_file.endswith('.kv'):
                Builder.load_file(os.path.join(kv_dir, kv_file))

if __name__ == '__main__':
    MainApp().run()
