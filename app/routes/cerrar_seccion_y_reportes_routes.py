from flask import Blueprint, redirect, url_for, flash, request, send_file
from app.services.cerrar_seccion_y_reportes_service import CerrarSeccionYReportesService
from app.http_errors import HTTP_BAD_REQUEST
import os

cerrar_reportar_bp = Blueprint('cerrar_reportar', __name__)
service = CerrarSeccionYReportesService()

@cerrar_reportar_bp.route('/cerrar-seccion/<int:section_id>', methods=['POST'])
def cerrar_seccion(section_id):
    try:
        success, message = service.cerrar_seccion(section_id)
        flash(message, "success" if success else "danger")
    except Exception as e:
        print("Error inesperado al cerrar sección:", e)
        flash("Ocurrió un error inesperado al cerrar la sección.", "danger")
    return redirect('/')

@cerrar_reportar_bp.route('/reporte/notas-seccion/<int:section_id>', methods=['POST'])
def reporte_notas_seccion(section_id):
    try:
        pdf_path = service.generar_reporte_notas_seccion(section_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash("No se pudo generar el reporte de notas de la sección.", "danger")
            return redirect('/')
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print("Error en reporte_notas_seccion:", e)
        flash("Ocurrió un error al generar el reporte de notas.", "danger")
        return redirect('/')

@cerrar_reportar_bp.route('/reporte/finales-seccion/<int:section_id>', methods=['POST'])
def reporte_finales_seccion(section_id):
    try:
        pdf_path = service.generar_reporte_notas_finales(section_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash("No se pudo generar el reporte de notas finales de la sección.", "danger")
            return redirect('/')
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print("Error en reporte_finales_seccion:", e)
        flash("Ocurrió un error al generar el reporte de notas finales.", "danger")
        return redirect('/')

@cerrar_reportar_bp.route('/reporte/certificado', methods=['POST'])
def certificado_por_alumno():
    try:
        section_id = request.form.get("section_id", type=int)
        student_id = request.form.get("student_id", type=int)

        if not section_id or not student_id:
            flash("Debe seleccionar un alumno y una sección válida.", "danger")
            return redirect('/')

        pdf_path = service.generar_certificado_por_alumno(section_id, student_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash("No se pudo generar el certificado del estudiante.", "danger")
            return redirect('/')
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print("Error en certificado_por_alumno:", e)
        flash("Ocurrió un error al generar el certificado del alumno.", "danger")
        return redirect('/')

@cerrar_reportar_bp.route('/reporte/resumen-estudiante/<int:student_id>', methods=['POST'])
def resumen_estudiante(student_id):
    try:
        pdf_path = service.generar_reporte_resumen_por_estudiante(student_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash("No se pudo generar el resumen del estudiante.", "danger")
            return redirect(f"/students/{student_id}")
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print("Error en resumen_estudiante:", e)
        flash("Ocurrió un error al generar el resumen del estudiante.", "danger")
        return redirect(f"/students/{student_id}")