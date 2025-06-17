# routes/evaluation_routes.py
from flask import Blueprint, render_template, request, redirect, flash
from app.services.evaluation_service import EvaluationService
from app.http_errors import HTTP_BAD_REQUEST

evaluation_bp = Blueprint('evaluation', __name__)
service = EvaluationService()

@evaluation_bp.route('/sections/<int:section_id>/evaluations')
def index(section_id):
    evaluations = service.get_all_evaluations_by_section(section_id)
    total_weight = service.get_total_weight_by_section(section_id)
    return render_template('evaluations/index.html', evaluations=evaluations, section_id=section_id, total_weight=total_weight)

@evaluation_bp.route('/sections/<int:section_id>/evaluations', methods=['POST'])
def create(section_id):
    try:
        type_ = request.form.get("type", "").strip()
        weight = float(request.form.get("weight", 0)) / 100
        optional = bool(int(request.form.get("optional", 0)))

        if not type_:
            flash("El tipo de evaluación es obligatorio.", "danger")
            return redirect(f"/sections/{section_id}/evaluations")

        current = service.get_total_weight_by_section(section_id)
        if current + weight > 1.01:
            flash("El peso total excede el 100%.", "danger")
            return redirect(f"/sections/{section_id}/evaluations")

        result = service.add_evaluation(section_id, type_, weight, optional)
        if not result["success"]:
            flash(result.get("message", "Error al crear la evaluación."), "danger")
        else:
            flash("Evaluación creada exitosamente.", "success")
        return redirect(f"/sections/{section_id}/evaluations")
    except Exception as e:
        print("Error en create:", e)
        flash("Error interno al crear evaluación.", "danger")
        return redirect(f"/sections/{section_id}/evaluations")

@evaluation_bp.route('/sections/<int:section_id>/evaluations/<int:eid>/delete', methods=['POST'])
def delete(section_id, eid):
    try:
        service.delete_evaluation(eid)
        flash("Evaluación eliminada correctamente.", "success")
        return redirect(f"/sections/{section_id}/evaluations")
    except Exception as e:
        print("Error al eliminar evaluación:", e)
        flash("Error interno al eliminar evaluación.", "danger")
        return redirect(f"/sections/{section_id}/evaluations")

@evaluation_bp.route('/sections/<int:section_id>/evaluations/<int:eid>/edit', methods=['POST'])
def update(section_id, eid):
    try:
        type_ = request.form.get("type", "").strip()
        weight = float(request.form.get("weight", 0)) / 100
        optional = bool(int(request.form.get("optional", 0)))

        if not type_:
            flash("El tipo de evaluación es obligatorio.", "danger")
            return redirect(f"/sections/{section_id}/evaluations")

        evaluations = service.get_all_evaluations_by_section(section_id)
        current = sum(e['weight'] for e in evaluations if e['id'] != eid)
        if current + weight > 1.01:
            flash("El peso total excede el 100%.", "danger")
            return redirect(f"/sections/{section_id}/evaluations")

        result = service.update_evaluation(eid, type_, weight, optional)
        if not result["success"]:
            flash(result.get("message", "Error al actualizar la evaluación."), "danger")
        else:
            flash("Evaluación actualizada exitosamente.", "success")
        return redirect(f"/sections/{section_id}/evaluations")
    except Exception as e:
        print("Error en update:", e)
        flash("Error interno al actualizar evaluación.", "danger")
        return redirect(f"/sections/{section_id}/evaluations")