from modelos.validaciones import hay_conflicto_horario


class GestorCitas:
    def __init__(self):
        self.__citas = []

    @property
    def citas(self) -> list:
        return list(self.__citas)

    # ── Operaciones CRUD ──────────────────────────────────────────────────────

    def agregar_cita(self, cita) -> bool:
        if hay_conflicto_horario(self.__citas, cita.doctor, cita.fecha, cita.hora):
            return False  # El llamador debe informar al usuario del conflicto

        self.__citas.append(cita)
        return True

    def obtener_cita(self, indice: int):
        if 0 <= indice < len(self.__citas):
            return self.__citas[indice]
        return None

    def modificar_cita(self, indice: int, nueva_fecha: str = None,
                       nueva_hora: str = None, nuevo_doctor=None,
                       nuevo_paciente=None) -> bool:
        cita = self.obtener_cita(indice)
        if cita is None:
            return False

        if cita.estado == 'cancelada':
            return False

        # Determina los valores finales usando el actual si no se pasa uno nuevo
        doctor_final = nuevo_doctor   or cita.doctor
        fecha_final  = nueva_fecha    or cita.fecha
        hora_final   = nueva_hora     or cita.hora

        # Verifica conflicto con el nuevo horario, excluyendo la cita actual
        if hay_conflicto_horario(self.__citas, doctor_final, fecha_final,
                                 hora_final, excluir_indice=indice):
            return False

        # Aplica los cambios solo si se proporcionaron nuevos valores
        if nueva_fecha or nueva_hora:
            cita.reprogramar(fecha_final, hora_final)
        if nuevo_doctor:
            cita.actualizar_doctor(nuevo_doctor)
        if nuevo_paciente:
            cita.actualizar_paciente(nuevo_paciente)

        return True

    # ── Listados ──────────────────────────────────────────────────────────────

    def listar_citas(self):
        if not self.__citas:
            print("  No hay citas registradas.")
            return

        sep = '─' * 82
        print(sep)
        print(f"  {'#':<4} {'Paciente':<22} {'Doctor':<22} {'Fecha':<12} {'Hora':<7} Estado")
        print(sep)
        for i, cita in enumerate(self.__citas, start=1):
            print(
                f"  {i:<4} {cita.paciente.nombre:<22} {cita.doctor.nombre:<22} "
                f"{cita.fecha:<12} {cita.hora:<7} {cita.estado.upper()}"
            )
        print(sep)
        print(f"  Total: {len(self.__citas)} cita(s) registrada(s).")
