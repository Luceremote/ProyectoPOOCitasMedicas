from modelos.usuario import Usuario


class Doctor(Usuario):
    def __init__(self, id: str, nombre: str, email: str, telefono: str, especialidad: str):
        super().__init__(id, nombre, email, telefono)
        self.__especialidad = especialidad

    # ── Propiedad ─────────────────────────────────────────────────────────────

    @property
    def especialidad(self) -> str:
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, valor: str):
        if not valor.strip():
            raise ValueError("La especialidad no puede estar vacía.")
        self.__especialidad = valor.strip()

    # ── Implementación de métodos abstractos de Usuario ───────────────────────

    def mostrar_informacion(self):
        print(f"  Tipo         : {self.obtener_tipo()}")
        print(f"  Nombre       : {self.nombre}")
        print(f"  ID           : {self.id}")
        print(f"  Especialidad : {self.especialidad}")
        print(f"  Teléfono     : {self.telefono}")
        print(f"  Email        : {self.email}")

    def obtener_tipo(self) -> str:
        return 'Doctor'

    def __str__(self) -> str:
        return f"{self.nombre}  |  {self.especialidad}"
