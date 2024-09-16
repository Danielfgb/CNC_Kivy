import serial
import time

class CNCController:
    def __init__(self, serial_ports, baud_rate=115200):
        self.serial_ports = serial_ports
        self.baud_rate = baud_rate
        self.grbl = None
        self.home_executed = False  # Para controlar si ya se fue a home la primera vez

    def connect(self):
        """Establece conexión con la CNC buscando en los puertos disponibles."""
        for port in self.serial_ports:
            try:
                self.grbl = serial.Serial(port, self.baud_rate)
                time.sleep(2)  
                print(f"Conectado a GRBL en {port}")
                break
            except serial.SerialException:
                print(f"No se pudo conectar a {port}. Probando siguiente puerto...")

        if not self.grbl:
            raise Exception("No se pudo conectar a ningún puerto serial.")

        # Resetear GRBL y desbloquear solo la primera vez
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
        """Envía un comando a GRBL e imprime el comando enviado."""
        print(f"Enviando comando: {command}")
        self.grbl.write(f"{command}\n".encode())
        time.sleep(0.1)
        return self.grbl.readline().strip()

    def go_home(self):
        """Mueve la máquina a la posición home."""
        if not self.home_executed:
            # Ir a home solo la primera vez
            self.send_command("$H")  # Enviar homing
            time.sleep(2)  # Esperar que se complete el homing
            self.send_command("$X")  # Desbloquear después del homing
            self.send_command("G92 X0 Y0 Z0")  # Establecer posición cero en la máquina
            self.home_executed = True
            print("Movido a home y desbloqueado.")
        else:
            # En siguientes ocasiones, mover directamente a la posición (0,0,0)
            self.move_to(x=0, y=0, z=0)

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

        # Mueve primero los ejes X e Y
        if x is not None or y is not None:
            self.move_to(x=x, y=y)  # Mover X e Y juntos
            print(f"Moviendo primero a X={x}, Y={y}...")
            # Esperar hasta que los ejes X e Y hayan alcanzado la posición
            self.wait_for_position_reached(x=x, y=y)

        # Luego mueve el eje Z
        if z is not None:
            self.move_to(z=z)  # Mover Z después
            print(f"Moviendo luego a Z={z}...")
            self.wait_for_position_reached(z=z)

    def wait_for_position_reached(self, x=None, y=None, z=None):
        """Espera hasta que los ejes hayan alcanzado las coordenadas indicadas."""
        while True:
            status = self.send_command("?")  # Obtener el estado de la máquina
            pos_str = status.decode().split('|')[1].replace('MPos:', '')
            positions = list(map(float, pos_str.split(',')))  # Convertir la posición en floats

            current_x, current_y, current_z = positions[0], positions[1], positions[2]

            # Verificar si X e Y (o Z) han alcanzado las coordenadas deseadas
            if (x is None or abs(current_x - x) < 0.01) and \
            (y is None or abs(current_y - y) < 0.01) and \
            (z is None or abs(current_z - z) < 0.01):
                break  # Si todas las coordenadas han sido alcanzadas, salir del bucle

            time.sleep(0.1)  # Esperar antes de verificar nuevamente


    def stop_all(self):
        """Función para detener todo movimiento de la CNC inmediatamente."""
        self.send_command("!")  # Feed hold para detener todos los movimientos de inmediato
        print("Movimiento detenido inmediatamente.")

    def disconnect(self):
        """Cierra la conexión serial con GRBL."""
        if self.grbl:
            self.grbl.close()
            print("Conexión cerrada.")
