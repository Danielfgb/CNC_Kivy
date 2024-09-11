import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class CameraController:
    def __init__(self, camera_id=0, update_interval=1.0 / 30):
        self.camera_id = camera_id
        self.capture = None
        self.update_interval = update_interval
        self.cross_position = None  # Permite ajustar la posici�n de la cruz

    def start_camera(self, camera_image_widget):
        """Inicia la captura de video desde la c�mara USB"""
        self.capture = cv2.VideoCapture(self.camera_id)
        if not self.capture.isOpened():
            # Si no se puede abrir la c�mara, carga la imagen predeterminada
            camera_image_widget.source = './app/resources/img/cam.png'
            return False
        
        # Configura la actualizaci�n del frame en un intervalo regular
        Clock.schedule_interval(lambda dt: self.update_frame(camera_image_widget), self.update_interval)
        return True

    def update_frame(self, camera_image_widget):
        """Actualiza el frame de la c�mara y lo muestra en la pantalla"""
        ret, frame = self.capture.read()
        if ret:
            # Convierte el frame de BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # A�adir la cruz en la imagen
            self.draw_cross(frame)

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
            camera_image_widget.source = './app/resources/img/cam.png'

    def draw_cross(self, frame, color=(255, 0, 0), thickness=2):
        """Dibuja una cruz en la imagen"""
        h, w, _ = frame.shape
        # Si no se ha definido una posici�n, se dibuja en el centro
        cx, cy = (w // 2, h // 2) if self.cross_position is None else self.cross_position

        # L�neas de la cruz
        cv2.line(frame, (cx - 30, cy), (cx + 30, cy), color, thickness)
        cv2.line(frame, (cx, cy - 30), (cx, cy + 30), color, thickness)

    def set_cross_position(self, x, y):
        """Establece la posici�n de la cruz"""
        self.cross_position = (x, y)

    def stop_camera(self):
        """Libera los recursos de la c�mara al detener la aplicaci�n"""
        if self.capture:
            self.capture.release()
