import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class CamaraController:
    def __init__(self, camera_id=0, fallback_image='./app/resources/img/cam.png'):
        self.camera_id = camera_id
        self.capture = None
        self.fallback_image = fallback_image

    def start_camera(self, camera_image_widget):
        """Inicia la captura de video desde la c�mara USB"""
        self.capture = cv2.VideoCapture(self.camera_id)
        if not self.capture.isOpened():
            # Si no se puede abrir la c�mara, carga la imagen predeterminada
            camera_image_widget.source = self.fallback_image
            return

        # Configura la actualizaci�n del frame en un intervalo regular
        Clock.schedule_interval(lambda dt: self.update_frame(camera_image_widget), 1.0 / 30)  # 30 FPS

    def update_frame(self, camera_image_widget):
        """Actualiza el frame de la c�mara y lo muestra en la pantalla"""
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
            camera_image_widget.texture = texture
        else:
            # Si no se puede capturar, muestra la imagen predeterminada
            camera_image_widget.source = self.fallback_image

    def stop_camera(self):
        """Libera los recursos de la c�mara"""
        if self.capture:
            self.capture.release()
