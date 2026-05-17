from datetime import datetime

# ── Constantes de configuración del negocio ───────────────────────────────────
FORMATO_FECHA  = '%d/%m/%Y'   # Ejemplo: 25/08/2026
FORMATO_HORA   = '%H:%M'       # Ejemplo: 09:30  (formato 24 horas)
HORA_INICIO    = 8             # 08:00 — inicio del horario de atención
HORA_FIN       = 18            # 18:00 — fin del horario de atención


# ── Validaciones de usuario ───────────────────────────────────────────────────

def validar_nombre(nombre: str) -> str:
    nombre_limpio = nombre.strip() if nombre else ''
    if not nombre_limpio:
        raise ValueError(
            "El nombre no puede estar vacío ni contener solo espacios."
        )
    return nombre_limpio


def validar_id(id_valor: str) -> str:
    """
    Verifica que el ID no esté vacío Y contenga SOLO dígitos.
    Lanza ValueError si está vacío o tiene letras/símbolos.
    """
    id_limpio = str(id_valor).strip() if id_valor else ''
    if not id_limpio:
        raise ValueError("El ID no puede estar vacío.")
    if not id_limpio.isdigit():
        raise ValueError(
            f"El ID debe contener solo números. "
            f"'{id_limpio}' tiene caracteres no válidos (letras o símbolos)."
        )
    return id_limpio


def validar_numerico(valor: str, campo: str = 'campo',
                     obligatorio: bool = True) -> str:
    """
    Verifica que un valor contenga SOLO dígitos del 0 al 9.

    Útil para campos como teléfono, documento, edad, etc.

    Parámetros:
        valor       : texto a validar.
        campo       : nombre del campo (se usa en el mensaje de error).
        obligatorio : si False, permite cadena vacía sin lanzar error.

    Retorna el valor limpio (sin espacios) si es válido.
    Lanza ValueError con mensaje descriptivo si no lo es.
    """
    valor_limpio = str(valor).strip() if valor else ''

    if not valor_limpio:
        if obligatorio:
            raise ValueError(f"El {campo} no puede estar vacío.")
        return ''   # Campo opcional vacío: se acepta

    if not valor_limpio.isdigit():
        raise ValueError(
            f"El {campo} debe contener solo números. "
            f"'{valor_limpio}' tiene caracteres no válidos (letras o símbolos)."
        )

    return valor_limpio


def validar_id_unico(id_valor: str, coleccion: list) -> None:
    if any(obj.id == id_valor for obj in coleccion):
        raise ValueError(
            f"El ID '{id_valor}' ya está registrado. Use un ID diferente."
        )


# ── Validaciones de cita ──────────────────────────────────────────────────────

def validar_fecha(fecha_str: str) -> str:
    fecha_str = fecha_str.strip() if fecha_str else ''

    # Verificar que el formato sea correcto
    try:
        fecha = datetime.strptime(fecha_str, FORMATO_FECHA)
    except ValueError:
        raise ValueError(
            f"Formato de fecha inválido: '{fecha_str}'. "
            f"Use DD/MM/AAAA — ejemplo: 25/08/2026."
        )

    # Verificar que no sea una fecha pasada (comparamos solo la fecha, sin horas)
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if fecha < hoy:
        raise ValueError(
            f"La fecha '{fecha_str}' ya pasó. "
            "No se permiten fechas anteriores a hoy."
        )

    return fecha_str


def validar_hora(hora_str: str) -> str:
    hora_str = hora_str.strip() if hora_str else ''

    # Verificar que el formato sea correcto
    try:
        hora = datetime.strptime(hora_str, FORMATO_HORA)
    except ValueError:
        raise ValueError(
            f"Formato de hora inválido: '{hora_str}'. "
            f"Use HH:MM en formato 24 horas — ejemplo: 09:30."
        )

    # Verificar que esté dentro del horario de atención
    if hora.hour < HORA_INICIO or hora.hour >= HORA_FIN:
        raise ValueError(
            f"Hora '{hora_str}' fuera del horario de atención. "
            f"Horario permitido: 08:00 a 18:00."
        )

    return hora_str


def hay_conflicto_horario(citas: list, doctor, fecha: str, hora: str,
                           excluir_indice: int = None) -> bool:
    for i, cita in enumerate(citas):
        # Saltar la cita que se está editando (para no conflictuar consigo misma)
        if excluir_indice is not None and i == excluir_indice:
            continue

        # Las citas canceladas no cuentan como ocupadas
        if cita.estado == 'cancelada':
            continue

        if cita.doctor.id == doctor.id and cita.fecha == fecha and cita.hora == hora:
            return True  # Conflicto encontrado

    return False  # Horario disponible
