from modelos.usuario import Usuario


class Paciente(Usuario):
    def __init__(self, id: str, nombre: str, email: str, telefono: str,
                 eps: str, fecha_nacimiento: str):
        super().__init__(id, nombre, email, telefono)
        self.__eps              = eps
        self.__fecha_nacimiento = fecha_nacimiento

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def eps(self) -> str:
        return self.__eps

    @eps.setter
    def eps(self, valor: str):
        if not valor.strip():
            raise ValueError("La EPS no puede estar vacía.")
        self.__eps = valor.strip()

    @property
    def fecha_nacimiento(self) -> str:
        return self.__fecha_nacimiento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor: str):
        self.__fecha_nacimiento = valor

    # ── Implementación de métodos abstractos de Usuario ───────────────────────

    def mostrar_informacion(self):
        print(f"  Tipo     : {self.obtener_tipo()}")
        print(f"  Nombre   : {self.nombre}")
        print(f"  ID (CC)  : {self.id}")
        print(f"  EPS      : {self.eps}")
        print(f"  Nac.     : {self.fecha_nacimiento}")
        print(f"  Teléfono : {self.telefono}")
        print(f"  Email    : {self.email}")

    def obtener_tipo(self) -> str:
        return 'Paciente'

    def __str__(self) -> str:
        return f"{self.nombre}  |  CC: {self.id}  |  EPS: {self.eps}"
