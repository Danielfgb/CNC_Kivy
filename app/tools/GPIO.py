# control de pines gpio 
# --Control de modulo relé
# ---- Activar moto bomba
# ---- Activación de Controladora CNC
import RPi.GPIO as GPIO
import time

# Configurar el modo de numeración de pines
GPIO.setmode(GPIO.BCM)

# Definir los pines GPIO que controlan los relés
RELE_PINS = [7, 3, 22, 25]

# Configurar los pines como salida
for pin in RELE_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Inicialmente todos los relés están apagados

# Función para encender y apagar los relés
def probar_reles():
    try:
        while True:
            # Encender los relés uno por uno
            for pin in RELE_PINS:
                GPIO.output(pin, GPIO.HIGH)
                print(f"Relé en pin {pin} encendido")
                time.sleep(1)  # Mantener el relé encendido por 1 segundo
                
                # Apagar el relé
                GPIO.output(pin, GPIO.LOW)
                print(f"Relé en pin {pin} apagado")
                time.sleep(1)  # Esperar 1 segundo antes de pasar al siguiente
    except KeyboardInterrupt:
        # Restablecer los pines GPIO al estado inicial
        GPIO.cleanup()

# Ejecutar la prueba de los relés
if __name__ == "__main__":
    probar_reles()
