from abc import ABC, abstractmethod
from modelos.validaciones import validar_id, validar_nombre


class Usuario(ABC):
    def __init__(self, id: str, nombre: str, email: str, telefono: str):
        # validar_id y validar_nombre están en modelos/validaciones.py
        # Lanzan ValueError si los datos no son válidos
        self.__id       = validar_id(id)
        self.__nombre   = validar_nombre(nombre)
        self.__email    = email
        self.__telefono = telefono

    # ── Propiedades (getters y setters) ──────────────────────────────────────
    # Las propiedades permiten controlar cómo se leen y escriben los atributos

    @property
    def id(self) -> str:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        if '@' not in valor:
            raise ValueError(f"Email inválido: '{valor}'. Debe contener '@'.")
        self.__email = valor

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor.isdigit():
            raise ValueError("El teléfono debe contener solo dígitos.")
        self.__telefono = valor

    # ── Métodos abstractos ────────────────────────────────────────────────────
    # Las subclases DEBEN implementar estos métodos o Python lanzará TypeError

    @abstractmethod
    def mostrar_informacion(self):
        pass

    @abstractmethod
    def obtener_tipo(self) -> str:
        pass

    def __str__(self) -> str:
        return f'{self.nombre} (ID: {self.id})'
