import serial
import time

class CNCController:
    def __init__(self, serial_ports, baud_rate=115200):
        self.serial_ports = serial_ports
        self.baud_rate = baud_rate
        self.grbl = None

    def connect(self):
        """Establece conexión con la CNC buscando en los puertos disponibles."""
        for port in self.serial_ports:
            try:
                self.grbl = serial.Serial(port, self.baud_rate)
                time.sleep(2)  # Esperar a que GRBL inicie
                print(f"Conectado a GRBL en {port}")
                break
            except serial.SerialException:
                print(f"No se pudo conectar a {port}. Probando siguiente puerto...")

        if not self.grbl:
            raise Exception("No se pudo conectar a ningún puerto serial.")

        # Resetear GRBL
        self.grbl.write(b"\r\n\r\n")
        time.sleep(2)
        self.grbl.flushInput()

        # Inicializar GRBL con los parámetros
        self.initialize_grbl()

    def initialize_grbl(self):
        """Envía los comandos de configuración inicial a GRBL."""
        init_commands = [
            "$0=10", "$1=255", "$2=0", "$3=1", "$4=0", "$5=0",
            "$6=0", "$10=18", "$11=0.010", "$12=0.002", "$13=0",
            "$20=0", "$21=0", "$22=1", "$23=3", "$24=100", "$25=2000.000",
            "$26=250", "$27=2", "$30=1000", "$31=0", "$32=0",
            "$100=40", "$101=80", "$102=120", "$110=4000.000", "$111=4000.000",
            "$112=800", "$120=50.000", "$121=50.000", "$122=50.000",
            "$130=200.000", "$131=200.000", "$132=200.000"
        ]
        
        for command in init_commands:
            self.send_command(command)
            time.sleep(0.1)

    def send_command(self, command):
        """Envía un comando a GRBL."""
        self.grbl.write(f"{command}\n".encode())
        time.sleep(0.1)
        return self.grbl.readline().strip()

    def go_home(self):
        """Mueve la máquina a la posición home y desbloquea después."""
        self.send_command("$H")  # Enviar homing
        time.sleep(2)  # Esperar que se complete el homing
        self.send_command("$X")  # Desbloquear después del homing
        print("Movido a home y desbloqueado.")

    def move_to(self, x=None, y=None, z=None):
        """Mueve los ejes a las coordenadas especificadas."""
        command = "G0"
        if x is not None:
            command += f" X{x}"
        if y is not None:
            command += f" Y{y}"
        if z is not None:
            command += f" Z{z}"
        self.send_command(command)
        print(f"Moviendo a X={x}, Y={y}, Z={z}...")

    def move_to_tag(self, tag_location):
        """Mueve los ejes a la ubicación de un tag evitando colisiones."""
        x, y, z = tag_location

        # Primero mueve los ejes X e Y, luego el eje Z
        self.move_to(x=x, y=y)
        time.sleep(2)  # Esperar a que se complete el movimiento de X e Y
        self.move_to(z=z)
        time.sleep(2)  # Esperar a que se complete el movimiento de Z

    def disconnect(self):
        """Cierra la conexión serial con GRBL."""
        if self.grbl:
            self.grbl.close()
            print("Conexión cerrada.")

