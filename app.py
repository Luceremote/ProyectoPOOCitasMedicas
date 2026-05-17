from flask import Flask, render_template, request, redirect, url_for, flash

from modelos.paciente import Paciente
from modelos.doctor import Doctor
from modelos.cita import Cita
import modelos.validaciones as val
from modelos.repositorio import (
    pacientes, doctores, gestor,
    buscar_paciente, buscar_doctor,
    eliminar_paciente as repo_eliminar_paciente,
    eliminar_doctor as repo_eliminar_doctor,
    contar_citas_activas_paciente, contar_citas_activas_doctor,
)


app = Flask(__name__)
app.secret_key = 'secret_key_123'


# ── Dashboard principal ───────────────────────────────────────────────────────

@app.route('/')
def index():
    """Página principal: muestra estadísticas, citas, pacientes y doctores.

    Pasa al template un mapa {id → nº citas activas} para que cada tarjeta
    de paciente/doctor muestre cuántas citas se cancelarían si se elimina.
    """
    citas_por_paciente = {
        p.id: contar_citas_activas_paciente(p.id) for p in pacientes
    }
    citas_por_doctor = {
        d.id: contar_citas_activas_doctor(d.id) for d in doctores
    }

    return render_template(
        'index.html',
        citas=gestor.citas,
        pacientes=pacientes,
        doctores=doctores,
        citas_por_paciente=citas_por_paciente,
        citas_por_doctor=citas_por_doctor,
    )


# ── Registro de pacientes ─────────────────────────────────────────────────────

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
def nuevo_paciente():
    """
    Registra un nuevo paciente y lo agrega DINÁMICAMENTE a la lista global.

    Una vez registrado, el paciente queda inmediatamente disponible en:
        - El listado del dashboard (/)
        - El select de pacientes al crear/editar una cita
    """
    if request.method == 'POST':
        # ── Recoger datos del formulario ──────────────────────────────────────
        id_p     = request.form.get('id', '').strip()
        nombre   = request.form.get('nombre', '').strip()
        email    = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        eps      = request.form.get('eps', '').strip()
        fecha_n  = request.form.get('fecha_nacimiento', '').strip()

        try:
            # ── Validar usando el módulo centralizado ─────────────────────────
            val.validar_id(id_p)                                 # solo dígitos
            val.validar_id_unico(id_p, pacientes)
            val.validar_nombre(nombre)
            val.validar_numerico(telefono, 'teléfono',
                                 obligatorio=False)              # solo dígitos

            if not eps:
                raise ValueError("La EPS no puede estar vacía.")

            # ── Crear y guardar en la lista compartida ────────────────────────
            nuevo = Paciente(id_p, nombre, email, telefono, eps, fecha_n)
            pacientes.append(nuevo)  # ← Aquí queda registrado dinámicamente

            flash(f"Paciente '{nombre}' registrado correctamente.", 'success')
            return redirect(url_for('index'))

        except ValueError as error:
            # Mostrar el error al usuario sin perder los datos ingresados
            flash(str(error), 'error')
            return render_template('paciente_form.html', datos=request.form)

    # GET: mostrar formulario vacío
    return render_template('paciente_form.html', datos=None)


# ── Registro de doctores ──────────────────────────────────────────────────────

@app.route('/doctores/nuevo', methods=['GET', 'POST'])
def nuevo_doctor():
    """
    Registra un nuevo doctor y lo agrega DINÁMICAMENTE a la lista global.

    Una vez registrado, queda inmediatamente disponible en el select
    de doctores al crear/editar una cita.
    """
    if request.method == 'POST':
        id_d         = request.form.get('id', '').strip()
        nombre       = request.form.get('nombre', '').strip()
        email        = request.form.get('email', '').strip()
        telefono     = request.form.get('telefono', '').strip()
        especialidad = request.form.get('especialidad', '').strip()

        try:
            val.validar_id(id_d)                                 # solo dígitos
            val.validar_id_unico(id_d, doctores)
            val.validar_nombre(nombre)
            val.validar_numerico(telefono, 'teléfono',
                                 obligatorio=False)              # solo dígitos

            if not especialidad:
                raise ValueError("La especialidad no puede estar vacía.")

            nuevo = Doctor(id_d, nombre, email, telefono, especialidad)
            doctores.append(nuevo)  # ← Disponible inmediatamente en el sistema

            flash(f"Doctor '{nombre}' registrado correctamente.", 'success')
            return redirect(url_for('index'))

        except ValueError as error:
            flash(str(error), 'error')
            return render_template('doctor_form.html', datos=request.form)

    return render_template('doctor_form.html', datos=None)


# ── Eliminación de pacientes y doctores ───────────────────────────────────────
# Usamos POST (no GET) para acciones destructivas: así no se ejecutan
# por accidente al cargar una URL o por un bot que rastree enlaces.

@app.route('/pacientes/<paciente_id>/eliminar', methods=['POST'])
def eliminar_paciente(paciente_id):
    """
    Elimina un paciente. Si tiene citas activas, las cancela en cascada
    antes de remover al paciente del listado.
    """
    resultado = repo_eliminar_paciente(paciente_id)

    if not resultado['ok']:
        flash(resultado['mensaje'], 'error')
        return redirect(url_for('index'))

    # Construir mensaje informativo con detalle de citas afectadas
    mensaje = resultado['mensaje']
    if resultado['citas_canceladas'] > 0:
        mensaje += (f" Se cancelaron {resultado['citas_canceladas']} "
                    f"cita(s) asociada(s).")
    flash(mensaje, 'success')
    return redirect(url_for('index'))


@app.route('/doctores/<doctor_id>/eliminar', methods=['POST'])
def eliminar_doctor(doctor_id):
    """
    Elimina un doctor. Si tiene citas activas, las cancela en cascada
    antes de remover al doctor del listado.
    """
    resultado = repo_eliminar_doctor(doctor_id)

    if not resultado['ok']:
        flash(resultado['mensaje'], 'error')
        return redirect(url_for('index'))

    mensaje = resultado['mensaje']
    if resultado['citas_canceladas'] > 0:
        mensaje += (f" Se cancelaron {resultado['citas_canceladas']} "
                    f"cita(s) asociada(s).")
    flash(mensaje, 'success')
    return redirect(url_for('index'))


# ── Gestión de citas ──────────────────────────────────────────────────────────

@app.route('/citas/nueva', methods=['GET', 'POST'])
def nueva_cita():
    """Crea una nueva cita. Lee pacientes y doctores desde la lista GLOBAL actual."""
    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        doctor_id   = request.form.get('doctor_id')
        fecha       = request.form.get('fecha', '').strip()
        hora        = request.form.get('hora', '').strip()

        paciente = buscar_paciente(paciente_id)
        doctor   = buscar_doctor(doctor_id)

        if not paciente or not doctor:
            flash('Debe seleccionar un paciente y un doctor.', 'error')
            return redirect(url_for('nueva_cita'))

        try:
            val.validar_fecha(fecha)
            val.validar_hora(hora)

            cita = Cita(paciente, doctor, fecha, hora)
            exito = gestor.agregar_cita(cita)

            if not exito:
                flash(
                    f"Conflicto: {doctor.nombre} ya tiene una cita el "
                    f"{fecha} a las {hora}.",
                    'error'
                )
                return redirect(url_for('nueva_cita'))

            flash('Cita creada correctamente.', 'success')
            return redirect(url_for('index'))

        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for('nueva_cita'))

    # GET: pasar las listas ACTUALES (con cualquier paciente recién registrado)
    return render_template(
        'cita_form.html',
        cita=None,
        pacientes=pacientes,
        doctores=doctores,
        action='Crear',
    )


@app.route('/citas/<int:indice>/editar', methods=['GET', 'POST'])
def editar_cita(indice):
    """Modifica una cita existente."""
    cita = gestor.obtener_cita(indice)
    if cita is None:
        flash('Cita no encontrada.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        doctor_id   = request.form.get('doctor_id')
        fecha       = request.form.get('fecha', '').strip()
        hora        = request.form.get('hora', '').strip()

        nuevo_paciente_obj = buscar_paciente(paciente_id)
        nuevo_doctor_obj   = buscar_doctor(doctor_id)

        if not nuevo_paciente_obj or not nuevo_doctor_obj:
            flash('Debe seleccionar un paciente y un doctor.', 'error')
            return redirect(url_for('editar_cita', indice=indice))

        try:
            val.validar_fecha(fecha)
            val.validar_hora(hora)

            exito = gestor.modificar_cita(
                indice,
                nueva_fecha    = fecha,
                nueva_hora     = hora,
                nuevo_paciente = nuevo_paciente_obj,
                nuevo_doctor   = nuevo_doctor_obj,
            )

            if not exito:
                flash(
                    'Conflicto de horario con el doctor seleccionado.',
                    'error'
                )
                return redirect(url_for('editar_cita', indice=indice))

            flash('Cita modificada correctamente.', 'success')
            return redirect(url_for('index'))

        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for('editar_cita', indice=indice))

    return render_template(
        'cita_form.html',
        cita=cita,
        pacientes=pacientes,
        doctores=doctores,
        action='Editar',
    )


@app.route('/citas/<int:indice>/cancelar')
def cancelar_cita(indice):
    """Cancela una cita (cambio de estado, no elimina el registro)."""
    cita = gestor.obtener_cita(indice)
    if cita:
        cita.cancelar()
        flash('Cita cancelada correctamente.', 'success')
    else:
        flash('Cita no encontrada.', 'error')
    return redirect(url_for('index'))


# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
