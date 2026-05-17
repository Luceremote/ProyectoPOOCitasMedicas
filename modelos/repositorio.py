from modelos.paciente import Paciente
from modelos.doctor import Doctor
from modelos.gestor_citas import GestorCitas


# ── Lista dinámica de pacientes ───────────────────────────────────────────────
# Pre-cargada con 2 pacientes de ejemplo para que el sistema no arranque vacío.
# Se modifica en tiempo de ejecución con: pacientes.append(nuevo_paciente)
pacientes = [
    Paciente('1053874854', 'Nicolas Olaya', 'nicolas@gmail.com',
             '3125879955', 'Nueva EPS', '22/12/1998'),
    Paciente('1053878558', 'Laura Méndez',  'laura@gmail.com',
             '3125879900', 'Sanitas',   '05/03/1995'),
]


# ── Lista dinámica de doctores ────────────────────────────────────────────────
# Pre-cargada con 2 doctores de ejemplo. Se modifica con .append().
doctores = [
    Doctor('1053878555', 'Dr. Lucero Arana', 'lucero@gmail.com',
           '3125879956', 'Neurología'),
    Doctor('1053878557', 'Dra. Camila Ríos', 'camila@gmail.com',
           '3125879957', 'Cardiología'),
]


# ── Gestor central de citas ───────────────────────────────────────────────────
# Una sola instancia compartida por todo el sistema.
gestor = GestorCitas()


# ── Funciones auxiliares de búsqueda ──────────────────────────────────────────
# Usadas tanto por app.py (Flask) como por main.py (consola).

def buscar_paciente(paciente_id: str):
    return next((p for p in pacientes if p.id == paciente_id), None)


def buscar_doctor(doctor_id: str):
    return next((d for d in doctores if d.id == doctor_id), None)


# ── Conteo de citas asociadas (para eliminación segura) ───────────────────────

def contar_citas_activas_paciente(paciente_id: str) -> int:
    """Cuenta citas NO canceladas asociadas a un paciente."""
    return sum(
        1 for c in gestor.citas
        if c.paciente.id == paciente_id and c.estado != 'cancelada'
    )


def contar_citas_activas_doctor(doctor_id: str) -> int:
    """Cuenta citas NO canceladas asociadas a un doctor."""
    return sum(
        1 for c in gestor.citas
        if c.doctor.id == doctor_id and c.estado != 'cancelada'
    )


# ── Eliminación de pacientes y doctores ───────────────────────────────────────
# Estrategia frente a citas asociadas:
#   - Cancela en cascada las citas activas del paciente/doctor.
#   - Las citas quedan en el historial con estado 'cancelada' (no se borran)
#     para preservar la trazabilidad del sistema.
#   - Luego elimina al paciente/doctor de la lista.
# Retornan un dict con el resultado de la operación para que la capa web
# pueda mostrar mensajes informativos al usuario.

def eliminar_paciente(paciente_id: str) -> dict:
    """
    Elimina un paciente del sistema, cancelando antes sus citas activas.

    Retorna un dict con:
        ok               : True si se eliminó, False si no se encontró.
        nombre           : nombre del paciente eliminado (si aplica).
        citas_canceladas : número de citas activas que fueron canceladas.
        mensaje          : descripción de lo ocurrido.
    """
    paciente = buscar_paciente(paciente_id)
    if paciente is None:
        return {
            'ok': False,
            'nombre': None,
            'citas_canceladas': 0,
            'mensaje': f"Paciente con ID '{paciente_id}' no encontrado.",
        }

    # Cancelar en cascada las citas activas (no se borran del historial)
    canceladas = 0
    for cita in gestor.citas:
        if cita.paciente.id == paciente_id and cita.estado != 'cancelada':
            cita.cancelar()
            canceladas += 1

    nombre = paciente.nombre
    pacientes.remove(paciente)  # ← Elimina del listado dinámico

    return {
        'ok': True,
        'nombre': nombre,
        'citas_canceladas': canceladas,
        'mensaje': f"Paciente '{nombre}' eliminado correctamente.",
    }


def eliminar_doctor(doctor_id: str) -> dict:
    """
    Elimina un doctor del sistema, cancelando antes sus citas activas.
    Misma estrategia que eliminar_paciente.
    """
    doctor = buscar_doctor(doctor_id)
    if doctor is None:
        return {
            'ok': False,
            'nombre': None,
            'citas_canceladas': 0,
            'mensaje': f"Doctor con ID '{doctor_id}' no encontrado.",
        }

    canceladas = 0
    for cita in gestor.citas:
        if cita.doctor.id == doctor_id and cita.estado != 'cancelada':
            cita.cancelar()
            canceladas += 1

    nombre = doctor.nombre
    doctores.remove(doctor)

    return {
        'ok': True,
        'nombre': nombre,
        'citas_canceladas': canceladas,
        'mensaje': f"Doctor '{nombre}' eliminado correctamente.",
    }
