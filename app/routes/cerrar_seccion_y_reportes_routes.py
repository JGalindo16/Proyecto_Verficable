from flask import Blueprint, redirect, url_for, flash, request, send_file
from app.services.cerrar_seccion_y_reportes_service import CerrarSeccionYReportesService
from app.http_errors import HTTP_BAD_REQUEST

cerrar_reportar_bp = Blueprint('cerrar_reportar', __name__)
service = CerrarSeccionYReportesService()

@cerrar_reportar_bp.route('/cerrar-seccion/<int:section_id>', methods=['POST'])
def cerrar_seccion(section_id):
    success, message = service.cerrar_seccion(section_id)
    flash(message, "success" if success else "danger")
    return redirect('/')

@cerrar_reportar_bp.route('/reporte/notas-seccion/<int:section_id>', methods=['POST'])
def reporte_notas_seccion(section_id):
    pdf_path = service.generar_reporte_notas_seccion(section_id)
    if not pdf_path:
        flash("No se pudo generar el reporte de notas de la sección.", "danger")
        return redirect('/')
    return send_file(pdf_path, as_attachment=True)

@cerrar_reportar_bp.route('/reporte/finales-seccion/<int:section_id>', methods=['POST'])
def reporte_finales_seccion(section_id):
    pdf_path = service.generar_reporte_notas_finales(section_id)
    if not pdf_path:
        flash("No se pudo generar el reporte de notas finales.", "danger")
        return redirect('/')
    return send_file(pdf_path, as_attachment=True)

@cerrar_reportar_bp.route('/reporte/certificado', methods=['POST'])
def certificado_por_alumno():
    section_id = request.form.get("section_id", type=int)
    student_id = request.form.get("student_id", type=int)

    if not section_id or not student_id:
        flash("Debe seleccionar un alumno y una sección válida.", "danger")
        return redirect('/')

    pdf_path = service.generar_certificado_por_alumno(section_id, student_id)
    if not pdf_path:
        flash("No se pudo generar el certificado del estudiante.", "danger")
        return redirect('/')
    return send_file(pdf_path, as_attachment=True)

@cerrar_reportar_bp.route('/reporte/resumen-estudiante/<int:student_id>', methods=['POST'])
def resumen_estudiante(student_id):
    pdf_path = service.generar_reporte_resumen_por_estudiante(student_id)
    if not pdf_path:
        flash("No se pudo generar el resumen del estudiante.", "danger")
        return redirect(f"/students/{student_id}")
    return send_file(pdf_path, as_attachment=True)