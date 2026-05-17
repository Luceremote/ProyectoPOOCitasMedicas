from modelos.paciente import Paciente
from modelos.doctor import Doctor
from modelos.cita import Cita
import modelos.validaciones as val   # Importamos el módulo completo para claridad

# ── Datos compartidos con la aplicación web ───────────────────────────────────
# Importamos las listas y el gestor desde modelos/repositorio.py
# para que la consola y la web operen sobre los MISMOS datos.
from modelos.repositorio import pacientes, doctores, gestor


# ── Funciones de utilidad ─────────────────────────────────────────────────────

def pausar():
    input("\n  Presione ENTER para continuar...")


def separador(caracter: str = '─', ancho: int = 50) -> str:
    return caracter * ancho


def pedir_dato(etiqueta: str, obligatorio: bool = True) -> str:
    while True:
        valor = input(f"  {etiqueta}: ").strip()
        if valor or not obligatorio:
            return valor
        print("  ⚠ Este campo es obligatorio. Intente de nuevo.")


def mostrar_menu():
    print("\n" + separador('═', 50))
    print("     SISTEMA DE GESTIÓN DE CLÍNICA MÉDICA")
    print(separador('═', 50))
    print("   1. Registrar paciente")
    print("   2. Registrar doctor")
    print("   3. Crear cita")
    print("   4. Modificar cita")
    print("   5. Ver pacientes")
    print("   6. Ver doctores")
    print("   7. Ver citas")
    print("   8. Salir")
    print(separador('═', 50))


# ── Funciones de selección (reutilizables) ────────────────────────────────────

def seleccionar_de_lista(coleccion: list, titulo: str):
    if not coleccion:
        print(f"\n  ⚠ No hay {titulo.lower()} registrados.")
        return None

    print(f"\n  {titulo} disponibles:")
    print(separador())
    for i, elemento in enumerate(coleccion, start=1):
        print(f"    {i}. {elemento}")
    print(separador())

    try:
        opcion = int(pedir_dato(f"Seleccione número (1-{len(coleccion)})"))
        if 1 <= opcion <= len(coleccion):
            return coleccion[opcion - 1]
        print("  ⚠ Número fuera de rango.")
    except ValueError:
        print("  ⚠ Debe ingresar un número entero.")

    return None


def buscar_citas_por_paciente(nombre_buscado: str) -> list:
    termino = nombre_buscado.lower()
    return [
        (i, c) for i, c in enumerate(gestor.citas)
        if termino in c.paciente.nombre.lower()
    ]


# ── Opción 1: Registrar paciente ──────────────────────────────────────────────

def registrar_paciente():
    print("\n" + separador('─', 50))
    print("  REGISTRAR NUEVO PACIENTE")
    print(separador('─', 50))

    try:
        # ── Validar ID ────────────────────────────────────────────────────────
        id_p = pedir_dato("ID (cédula)")
        val.validar_id(id_p)
        val.validar_id_unico(id_p, pacientes)   # Verifica que no esté repetido

        # ── Validar nombre ────────────────────────────────────────────────────
        nombre = pedir_dato("Nombre completo")
        val.validar_nombre(nombre)

        # ── Resto de datos ────────────────────────────────────────────────────
        email    = pedir_dato("Email")
        telefono = pedir_dato("Teléfono")
        eps      = pedir_dato("EPS (entidad de salud)")
        fecha_n  = pedir_dato("Fecha de nacimiento (DD/MM/AAAA)")

        # Crea el paciente y lo agrega a la lista global
        nuevo = Paciente(id_p, nombre, email, telefono, eps, fecha_n)
        pacientes.append(nuevo)

        print(f"\n  ✔ Paciente '{nombre}' registrado exitosamente.")

    except ValueError as error:
        # Si algo falla, mostramos el mensaje de error sin cerrar el programa
        print(f"\n  ✘ Error de validación: {error}")


# ── Opción 2: Registrar doctor ────────────────────────────────────────────────

def registrar_doctor():
    print("\n" + separador('─', 50))
    print("  REGISTRAR NUEVO DOCTOR")
    print(separador('─', 50))

    try:
        # ── Validar ID ────────────────────────────────────────────────────────
        id_d = pedir_dato("ID")
        val.validar_id(id_d)
        val.validar_id_unico(id_d, doctores)   # Verifica que no esté repetido

        # ── Validar nombre ────────────────────────────────────────────────────
        nombre = pedir_dato("Nombre completo (incluya Dr. / Dra.)")
        val.validar_nombre(nombre)

        # ── Resto de datos ────────────────────────────────────────────────────
        email        = pedir_dato("Email")
        telefono     = pedir_dato("Teléfono")
        especialidad = pedir_dato("Especialidad médica")

        # Crea el doctor y lo agrega a la lista global
        nuevo = Doctor(id_d, nombre, email, telefono, especialidad)
        doctores.append(nuevo)

        print(f"\n  ✔ Doctor '{nombre}' registrado exitosamente.")

    except ValueError as error:
        print(f"\n  ✘ Error de validación: {error}")


# ── Opción 3: Crear cita ──────────────────────────────────────────────────────

def crear_cita():
    print("\n" + separador('─', 50))
    print("  CREAR NUEVA CITA")
    print(separador('─', 50))

    try:
        # ── Seleccionar paciente ──────────────────────────────────────────────
        paciente = seleccionar_de_lista(pacientes, "Pacientes")
        if paciente is None:
            return

        # ── Seleccionar doctor ────────────────────────────────────────────────
        doctor = seleccionar_de_lista(doctores, "Doctores")
        if doctor is None:
            return

        # ── Fecha ─────────────────────────────────────────────────────────────
        fecha = pedir_dato("Fecha de la cita (DD/MM/AAAA, ej: 25/08/2026)")
        val.validar_fecha(fecha)   # Lanza ValueError si es pasada o mal formateada

        # ── Hora ──────────────────────────────────────────────────────────────
        hora = pedir_dato("Hora de la cita (HH:MM en 24h, ej: 09:30)")
        val.validar_hora(hora)    # Lanza ValueError si está fuera del horario

        # ── Crear y guardar la cita ───────────────────────────────────────────
        nueva_cita = Cita(paciente, doctor, fecha, hora)
        exito = gestor.agregar_cita(nueva_cita)

        if exito:
            print(f"\n  ✔ Cita creada: {paciente.nombre} → {doctor.nombre} | {fecha} {hora}")
        else:
            print(f"\n  ✘ Conflicto: {doctor.nombre} ya tiene cita el {fecha} a las {hora}.")

    except ValueError as error:
        print(f"\n  ✘ Error de validación: {error}")


# ── Opción 4: Modificar cita ──────────────────────────────────────────────────

def modificar_cita():
    print("\n" + separador('─', 50))
    print("  MODIFICAR CITA")
    print(separador('─', 50))

    citas_actuales = gestor.citas
    if not citas_actuales:
        print("  ⚠ No hay citas registradas.")
        return

    # ── Buscar la cita ────────────────────────────────────────────────────────
    print("  ¿Cómo desea buscar la cita?")
    print("    1. Por número de cita en el listado")
    print("    2. Por nombre del paciente")
    modo = pedir_dato("Opción")

    indice_cita = None   # Guardará el índice (base 0) de la cita a modificar

    if modo == '1':
        # Mostrar el listado y pedir número
        gestor.listar_citas()
        try:
            num = int(pedir_dato(f"Número de cita (1-{len(citas_actuales)})"))
            if 1 <= num <= len(citas_actuales):
                indice_cita = num - 1
            else:
                print("  ⚠ Número fuera de rango.")
                return
        except ValueError:
            print("  ⚠ Debe ingresar un número entero.")
            return

    elif modo == '2':
        # Buscar por nombre (parcial)
        nombre_buscado = pedir_dato("Nombre del paciente (o parte del nombre)")
        resultados = buscar_citas_por_paciente(nombre_buscado)

        if not resultados:
            print(f"  ⚠ No se encontraron citas para '{nombre_buscado}'.")
            return

        print(f"\n  Citas encontradas para '{nombre_buscado}':")
        print(separador())
        for pos, (i, c) in enumerate(resultados, start=1):
            print(f"    {pos}. [{c.estado.upper()}] {c.paciente.nombre} → "
                  f"{c.doctor.nombre} | {c.fecha} {c.hora}")
        print(separador())

        try:
            sel = int(pedir_dato(f"Seleccione número (1-{len(resultados)})"))
            if 1 <= sel <= len(resultados):
                indice_cita = resultados[sel - 1][0]
            else:
                print("  ⚠ Número fuera de rango.")
                return
        except ValueError:
            print("  ⚠ Debe ingresar un número entero.")
            return
    else:
        print("  ⚠ Opción inválida.")
        return

    # ── Verificar que la cita se puede modificar ──────────────────────────────
    cita = gestor.obtener_cita(indice_cita)
    if cita is None:
        print("  ⚠ Cita no encontrada.")
        return

    if cita.estado == 'cancelada':
        print("  ⚠ No se puede modificar una cita cancelada.")
        return

    # ── Mostrar datos actuales ────────────────────────────────────────────────
    print("\n  Datos actuales de la cita:")
    cita.mostrar_cita()

    # ── Menú de campos a modificar ────────────────────────────────────────────
    print("  ¿Qué desea modificar?")
    print("    1. Fecha y hora")
    print("    2. Doctor")
    print("    3. Paciente")
    print("    4. Todo lo anterior")
    sub_opcion = pedir_dato("Opción")

    nueva_fecha    = None
    nueva_hora     = None
    nuevo_doctor   = None
    nuevo_paciente = None

    try:
        # ── Modificar fecha y hora ────────────────────────────────────────────
        if sub_opcion in ('1', '4'):
            print(f"  (Deje vacío para mantener el valor actual: {cita.fecha})")
            entrada_fecha = pedir_dato("Nueva fecha (DD/MM/AAAA)", obligatorio=False)
            if entrada_fecha:
                val.validar_fecha(entrada_fecha)
                nueva_fecha = entrada_fecha

            print(f"  (Deje vacío para mantener el valor actual: {cita.hora})")
            entrada_hora = pedir_dato("Nueva hora (HH:MM)", obligatorio=False)
            if entrada_hora:
                val.validar_hora(entrada_hora)
                nueva_hora = entrada_hora

        # ── Modificar doctor ──────────────────────────────────────────────────
        if sub_opcion in ('2', '4'):
            print("\n  Seleccione el nuevo doctor:")
            nuevo_doctor = seleccionar_de_lista(doctores, "Doctores")

        # ── Modificar paciente ────────────────────────────────────────────────
        if sub_opcion in ('3', '4'):
            print("\n  Seleccione el nuevo paciente:")
            nuevo_paciente = seleccionar_de_lista(pacientes, "Pacientes")

        if sub_opcion not in ('1', '2', '3', '4'):
            print("  ⚠ Opción inválida.")
            return

        # ── Aplicar cambios ───────────────────────────────────────────────────
        exito = gestor.modificar_cita(
            indice_cita,
            nueva_fecha    = nueva_fecha,
            nueva_hora     = nueva_hora,
            nuevo_doctor   = nuevo_doctor,
            nuevo_paciente = nuevo_paciente,
        )

        if exito:
            print("\n  ✔ Cita modificada exitosamente.")
            print("  Nuevos datos:")
            gestor.obtener_cita(indice_cita).mostrar_cita()
        else:
            print("\n  ✘ No se pudo modificar: conflicto de horario con el doctor seleccionado.")

    except ValueError as error:
        print(f"\n  ✘ Error de validación: {error}")


# ── Opción 5: Ver pacientes ───────────────────────────────────────────────────

def ver_pacientes():
    """Muestra un listado completo de todos los pacientes registrados."""
    print("\n" + separador('─', 50))
    print("  LISTADO DE PACIENTES")
    print(separador('─', 50))

    if not pacientes:
        print("  No hay pacientes registrados.")
        return

    sep = separador('─', 80)
    print(f"\n{sep}")
    print(f"  {'#':<4} {'Nombre':<24} {'ID (CC)':<14} {'EPS':<16} {'Tel.':<14} Nac.")
    print(sep)
    for i, p in enumerate(pacientes, start=1):
        print(
            f"  {i:<4} {p.nombre:<24} {p.id:<14} {p.eps:<16} "
            f"{p.telefono:<14} {p.fecha_nacimiento}"
        )
    print(sep)
    print(f"  Total: {len(pacientes)} paciente(s) registrado(s).")


# ── Opción 6: Ver doctores ────────────────────────────────────────────────────

def ver_doctores():
    """Muestra un listado completo de todos los doctores registrados."""
    print("\n" + separador('─', 50))
    print("  LISTADO DE DOCTORES")
    print(separador('─', 50))

    if not doctores:
        print("  No hay doctores registrados.")
        return

    sep = separador('─', 75)
    print(f"\n{sep}")
    print(f"  {'#':<4} {'Nombre':<26} {'Especialidad':<20} {'ID':<14} Teléfono")
    print(sep)
    for i, d in enumerate(doctores, start=1):
        print(
            f"  {i:<4} {d.nombre:<26} {d.especialidad:<20} "
            f"{d.id:<14} {d.telefono}"
        )
    print(sep)
    print(f"  Total: {len(doctores)} doctor(es) registrado(s).")


# ── Opción 7: Ver citas ───────────────────────────────────────────────────────

def ver_citas():
    """Muestra el listado completo de citas usando el método del gestor."""
    print("\n" + separador('─', 50))
    print("  LISTADO DE CITAS")
    print(separador('─', 50))
    gestor.listar_citas()


# ── Bucle principal del menú ──────────────────────────────────────────────────

def ejecutar_menu():
    # Diccionario que mapea cada opción a su función correspondiente
    # Esto evita una cadena larga de if/elif
    opciones = {
        '1': registrar_paciente,
        '2': registrar_doctor,
        '3': crear_cita,
        '4': modificar_cita,
        '5': ver_pacientes,
        '6': ver_doctores,
        '7': ver_citas,
    }

    print("\n  Bienvenido al Sistema de Gestión de Clínica Médica.")

    while True:
        try:
            mostrar_menu()
            opcion = input("\n  Seleccione una opción (1-8): ").strip()

            if opcion == '8':
                print("\n  Hasta luego. ¡Que tenga un excelente día!\n")
                break

            accion = opciones.get(opcion)
            if accion:
                accion()                  # Ejecuta la función del menú
            else:
                print("\n  ⚠ Opción inválida. Por favor elija un número del 1 al 8.")

        except KeyboardInterrupt:
            # El usuario presionó Ctrl+C — salimos limpiamente
            print("\n\n  Programa interrumpido. ¡Hasta luego!\n")
            break
        except Exception as error:
            # Captura cualquier error inesperado para que el programa no se cierre
            print(f"\n  ✘ Error inesperado: {error}")
            print("     El sistema continúa funcionando.")

        pausar()


# ── Punto de entrada ──────────────────────────────────────────────────────────
# Este bloque se ejecuta solo cuando corremos 'python main.py' directamente,
# no cuando este archivo es importado por otro módulo.

if __name__ == '__main__':
    ejecutar_menu()
