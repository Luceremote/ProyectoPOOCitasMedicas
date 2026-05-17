class Cita:
    # Constante de clase: estados válidos para referencia y validación
    ESTADOS = ('pendiente', 'confirmada', 'cancelada')

    def __init__(self, paciente, doctor, fecha: str, hora: str):
        self.__paciente = paciente
        self.__doctor   = doctor
        self.__fecha    = fecha
        self.__hora     = hora
        self.__estado   = 'pendiente'  # Toda cita inicia como pendiente

    # ── Propiedades de solo lectura ───────────────────────────────────────────

    @property
    def paciente(self):
        return self.__paciente

    @property
    def doctor(self):
        return self.__doctor

    @property
    def fecha(self) -> str:
        return self.__fecha

    @property
    def hora(self) -> str:
        return self.__hora

    @property
    def estado(self) -> str:
        return self.__estado

    # ── Métodos de acción ─────────────────────────────────────────────────────

    def confirmar(self):
        if self.__estado == 'cancelada':
            raise ValueError("No se puede confirmar una cita que ya fue cancelada.")
        self.__estado = 'confirmada'

    def cancelar(self):
        self.__estado = 'cancelada'

    def reprogramar(self, nueva_fecha: str, nueva_hora: str):
        if self.__estado == 'cancelada':
            raise ValueError("No se puede reprogramar una cita cancelada.")
        self.__fecha = nueva_fecha
        self.__hora  = nueva_hora

    def actualizar_doctor(self, doctor):
        if self.__estado == 'cancelada':
            raise ValueError("No se puede modificar una cita cancelada.")
        self.__doctor = doctor

    def actualizar_paciente(self, paciente):
        if self.__estado == 'cancelada':
            raise ValueError("No se puede modificar una cita cancelada.")
        self.__paciente = paciente

    def mostrar_cita(self):
        separador = '─' * 45
        print(separador)
        print(f"  Paciente     : {self.paciente.nombre}")
        print(f"  Doctor       : {self.doctor.nombre}")
        print(f"  Especialidad : {self.doctor.especialidad}")
        print(f"  Fecha        : {self.fecha}")
        print(f"  Hora         : {self.hora}")
        print(f"  Estado       : {self.estado.upper()}")
        print(separador)

    def __str__(self) -> str:
        return (
            f"{self.paciente.nombre:<22} → {self.doctor.nombre:<22} "
            f"| {self.fecha}  {self.hora}  [{self.estado.upper()}]"
        )
