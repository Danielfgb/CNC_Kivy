import serial
import time

class GRBLController:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.current_position = [0, 0, 0]  # X, Y, Z
        self.max_position = [200, 200, -40]  # Máximos en X, Y, Z
        
        # Inicializar el controlador
        self._initialize()
        
        # Configuración inicial con finales de carrera habilitados
        self.init_grbl()

    def _initialize(self):
        """Inicializa el controlador, asegurándose de que la comunicación esté establecida."""
        print("Inicializando el controlador GRBL...")
        self.serial.flushInput()  # Limpiar el buffer de entrada
        self.serial.flushOutput() # Limpiar el buffer de salida
        time.sleep(1)  # Esperar para asegurar que la comunicación esté establecida

    def _send_command(self, command):
        """Envía un comando a GRBL y lee la respuesta."""
        print(f"Enviando comando: {command}")
        self.serial.write(f"{command}\n".encode())
        return self.serial.readlines()

    def init_grbl(self):
        """Inicializa GRBL con la configuración proporcionada."""
        init_commands = """
        $0=10
        $1=255
        $2=0
        $3=1
        $4=0
        $5=0
        $6=0
        $10=18
        $11=0.010
        $12=0.002
        $13=0
        $20=1    # Activa los límites duros
        $21=0
        $22=1
        $23=3
        $24=100
        $25=2000.000
        $26=250
        $27=2
        $30=1000
        $31=0
        $32=0
        $100=40
        $101=80
        $102=120
        $110=4000.000
        $111=4000.000
        $112=800
        $120=50.000
        $121=50.000
        $122=50.000
        $130=200.000
        $131=200.000
        $132=200.000
        """
        for command in init_commands.strip().split('\n'):
            response = self._send_command(command)
            print(f"Respuesta de GRBL al inicializar: {response}")

    def home(self):
        """Envía el comando para llevar los ejes a la posición home."""
        response = self._send_command('$H')
        print(f"Respuesta de GRBL: {response}")
        # Reiniciamos la posición a 0,0,0 después del home
        self.current_position = [0, 0, 0]

    def move_to(self, x=None, y=None, z=None):
        """Mueve los ejes de manera incremental y actualiza la posición."""
        if x is not None:
            # Asegurarse de que no se exceda el máximo
            target_x = min(self.max_position[0], max(0, self.current_position[0] + x))
            self.current_position[0] = target_x
        
        if y is not None:
            target_y = min(self.max_position[1], max(0, self.current_position[1] + y))
            self.current_position[1] = target_y

        if z is not None:
            target_z = min(self.max_position[2], max(0, self.current_position[2] + z))
            self.current_position[2] = target_z
        
        # Enviar comando G0 para mover los ejes
        command = f"G0 X{self.current_position[0]} Y{self.current_position[1]} Z{self.current_position[2]}"
        response = self._send_command(command)
        print(f"Respuesta de GRBL: {response}")
        print(f"Posición actual: {self.current_position}")

    def move_to_location(self, location):
        """Mueve los ejes a una ubicación específica."""
        x, y, z = location
        # Mover a las coordenadas absolutas especificadas
        command = f"G0 X{x} Y{y} Z{z}"
        response = self._send_command(command)
        self.current_position = [x, y, z]
        print(f"Respuesta de GRBL al mover a la posición {location}: {response}")

    def disable_motors(self):
        """Desactiva los motores."""
        self._send_command('M84')

    def run(self):
        """Corre el ciclo principal para mover los ejes según entradas del usuario."""
        print("Conectado a GRBL. Presiona 'h' para ir a Home, 'm' para ir al límite, 'z' para ir a la posición [99.8, 36, 0], o flechas para mover los ejes.")
        while True:
            command = input("Comando: ").lower()

            if command == 'h':
                self.home()
                print("Posición actual después de home: ", self.current_position)

            elif command == 'm':
                # Ir al máximo [200, 200, 200]
                self.move_to_location([200, 200, -40])

            elif command == 'z':
                # Ir a la ubicación específica [99.8, 36, 0]
                self.move_to_location([99.8, 36, 0])

            elif command == 'w':
                # Mover X +20 mm
                self.move_to(x=20)

            elif command == 's':
                # Mover X -20 mm
                self.move_to(x=-20)

            elif command == 'a':
                # Mover Y +20 mm
                self.move_to(y=20)

            elif command == 'd':
                # Mover Y -20 mm
                self.move_to(y=-20)

            elif command == 'q':
                # Mover Z +20 mm
                self.move_to(z=20)

            elif command == 'e':
                # Mover Z -20 mm
                self.move_to(z=-20)

            elif command == 'exit':
                # Deshabilitar motores y salir
                self.disable_motors()
                print("Motores deshabilitados. Cerrando conexión.")
                break

if __name__ == "__main__":
    controller = GRBLController(port='/dev/ttyUSB0')
    controller.run()
