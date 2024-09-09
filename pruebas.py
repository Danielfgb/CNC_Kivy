import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class CameraApp(App):
    def build(self):
        # Abre el dispositivo de video
        self.capture = cv2.VideoCapture('/dev/video0')
        if not self.capture.isOpened():
            print("Error: No se pudo abrir el dispositivo de video.")
            return

        # Configura el widget de imagen
        self.image = Image()
        layout = BoxLayout()
        layout.add_widget(self.image)

        # Programar la actualizaci�n de la imagen
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # Actualiza a 30 fps
        return layout

    def update(self, *args):
        ret, frame = self.capture.read()
        if ret:
            # Convierte el frame de BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Crea una textura de Kivy a partir del frame
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), bufferfmt='ubyte', colorfmt='rgb')
            self.image.texture = texture
        else:
            print("Error: No se pudo leer el frame del dispositivo de video.")

    def on_stop(self):
        self.capture.release()  # Libera la c�mara cuando la aplicaci�n se cierra

if __name__ == '__main__':
    CameraApp().run()
