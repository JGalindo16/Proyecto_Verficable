from flask import Blueprint, redirect, flash, request, send_file
from app.services.cerrar_seccion_y_reportes_service import CerrarSeccionYReportesService
from app.alertas.cerrar_seccion_y_routes_y_reportes_alerts import (
    ERROR_CIERRE_SECCION,
    REPORTE_NOTAS_NO_GENERADO,
    ERROR_REPORTE_NOTAS,
    REPORTE_FINALES_NO_GENERADO,
    ERROR_REPORTE_FINALES,
    CERTIFICADO_NO_GENERADO,
    ERROR_CERTIFICADO,
    CERTIFICADO_PARAMETROS_INVALIDOS,
    RESUMEN_ESTUDIANTE_NO_GENERADO,
    ERROR_RESUMEN_ESTUDIANTE
)
import os

cerrar_reportar_bp = Blueprint('cerrar_reportar', __name__)
service = CerrarSeccionYReportesService()

@cerrar_reportar_bp.route('/cerrar-seccion/<int:section_id>', methods=['POST'])
def cerrar_seccion(section_id):
    try:
        success, message = service.cerrar_seccion(section_id)
        flash(message, "success" if success else "danger")
    except Exception:
        flash(ERROR_CIERRE_SECCION, "danger")
    return redirect('/')

@cerrar_reportar_bp.route('/reporte/notas-seccion/<int:section_id>', methods=['POST'])
def reporte_notas_seccion(section_id):
    try:
        pdf_path = service.generar_reporte_notas_seccion(section_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash(REPORTE_NOTAS_NO_GENERADO, "danger")
            return redirect('/')
        return send_file(pdf_path, as_attachment=True)
    except Exception:
        flash(ERROR_REPORTE_NOTAS, "danger")
        return redirect('/')

@cerrar_reportar_bp.route('/reporte/finales-seccion/<int:section_id>', methods=['POST'])
def reporte_finales_seccion(section_id):
    try:
        pdf_path = service.generar_reporte_notas_finales(section_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash(REPORTE_FINALES_NO_GENERADO, "danger")
            return redirect('/')
        return send_file(pdf_path, as_attachment=True)
    except Exception:
        flash(ERROR_REPORTE_FINALES, "danger")
        return redirect('/')

@cerrar_reportar_bp.route('/reporte/certificado', methods=['POST'])
def certificado_por_alumno():
    try:
        section_id = request.form.get("section_id", type=int)
        student_id = request.form.get("student_id", type=int)

        if not section_id or not student_id:
            flash(CERTIFICADO_PARAMETROS_INVALIDOS, "danger")
            return redirect('/')

        pdf_path = service.generar_certificado_por_alumno(section_id, student_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash(CERTIFICADO_NO_GENERADO, "danger")
            return redirect('/')
        return send_file(pdf_path, as_attachment=True)
    except Exception:
        flash(ERROR_CERTIFICADO, "danger")
        return redirect('/')

@cerrar_reportar_bp.route('/reporte/resumen-estudiante/<int:student_id>', methods=['POST'])
def resumen_estudiante(student_id):
    try:
        pdf_path = service.generar_reporte_resumen_por_estudiante(student_id)
        if not pdf_path or not os.path.exists(pdf_path):
            flash(RESUMEN_ESTUDIANTE_NO_GENERADO, "danger")
            return redirect(f"/students/{student_id}")
        return send_file(pdf_path, as_attachment=True)
    except Exception:
        flash(ERROR_RESUMEN_ESTUDIANTE, "danger")
        return redirect(f"/students/{student_id}")
