from flask import Blueprint, send_file, flash, render_template
from app.services.generar_horario_service import GenerarHorarioService

generar_horario_bp = Blueprint('generar_horario', __name__)

@generar_horario_bp.route('/generar-horario', methods=['POST'])
def generar_horario():
    service = GenerarHorarioService()
    success, response = service.generar()
    if success:
        flash("Horario generado correctamente.", "success")
        return send_file(
            response,
            as_attachment=True,
            download_name="horario_generado.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        flash(f"Error al generar horario: {response}", "danger")
        return render_template('global/home.html')
