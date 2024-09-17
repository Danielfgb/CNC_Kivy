import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class CameraController:
    def __init__(self, camera_id=0, update_interval=1.0 / 30):
        self.camera_id = camera_id
        self.capture = None
        self.update_interval = update_interval
        self.cross_position = None  # Permite ajustar la posición de la cruz
        self.zoom_enabled = False  # Controla el estado del zoom

    def start_camera(self, camera_image_widget):
        """Inicia la captura de video desde la cámara USB"""
        self.capture = cv2.VideoCapture(self.camera_id)
        if not self.capture.isOpened():
            # Si no se puede abrir la cámara, carga la imagen predeterminada
            camera_image_widget.source = './app/resources/img/cam.png'
            return False
        
        # Configura la actualización del frame en un intervalo regular
        Clock.schedule_interval(lambda dt: self.update_frame(camera_image_widget), self.update_interval)
        return True

    def update_frame(self, camera_image_widget):
        """Actualiza el frame de la cámara y lo muestra en la pantalla"""
        ret, frame = self.capture.read()
        if ret:
            # Convierte el frame de BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Realizar zoom si está habilitado
            if self.zoom_enabled:
                frame = self.apply_zoom(frame)

            # Añadir la cruz en la imagen
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

    def apply_zoom(self, frame, zoom_factor=2):
        """Aplica un zoom a la imagen recortando el centro y escalando"""
        h, w, _ = frame.shape
        center_x, center_y = w // 2, h // 2
        new_w, new_h = w // zoom_factor, h // zoom_factor

        # Recortar la imagen centrada
        frame_cropped = frame[center_y - new_h // 2:center_y + new_h // 2,
                              center_x - new_w // 2:center_x + new_w // 2]
        # Escalar la imagen de nuevo a su tamaño original
        return cv2.resize(frame_cropped, (w, h))

    def toggle_zoom(self):
        """Alterna el estado del zoom"""
        self.zoom_enabled = not self.zoom_enabled

    def draw_cross(self, frame, color=(255, 0, 0), thickness=2):
        """Dibuja una cruz en la imagen"""
        h, w, _ = frame.shape
        # Si no se ha definido una posición, se dibuja en el centro
        cx, cy = (w // 2, h // 2) if self.cross_position is None else self.cross_position

        # Líneas de la cruz
        cv2.line(frame, (cx - 30, cy), (cx + 30, cy), color, thickness)
        cv2.line(frame, (cx, cy - 30), (cx, cy + 30), color, thickness)

    def set_cross_position(self, x, y):
        """Establece la posición de la cruz"""
        self.cross_position = (x, y)

    def stop_camera(self):
        """Libera los recursos de la cámara al detener la aplicación"""
        if self.capture:
            self.capture.release()



#on_touch_down: root.camera_controller.toggle_zoom()
