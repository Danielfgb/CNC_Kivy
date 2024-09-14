# control de pines gpio 
# --Control de modulo relé
# ---- Activar moto bomba
# ---- Activación de Controladora CNC
import RPi.GPIO as GPIO

class GPIOController:
    def __init__(self):
        self.pin_cnc = 22  # Pin para la CNC
        # Configurar el GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_cnc, GPIO.OUT)
        self.deactivate_cnc()  # Asegurarse de que la CNC esté desactivada al iniciar

    def activate_cnc(self):
        """Activa el relé para la CNC."""
        GPIO.output(self.pin_cnc, GPIO.HIGH)
        print(f"CNC activada en el pin {self.pin_cnc}")

    def deactivate_cnc(self):
        """Desactiva el relé para la CNC."""
        GPIO.output(self.pin_cnc, GPIO.LOW)
        print(f"CNC desactivada en el pin {self.pin_cnc}")

    def cleanup(self):
        """Limpia los pines GPIO al finalizar."""
        GPIO.cleanup()
        print("GPIO limpiado")
