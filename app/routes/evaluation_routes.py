from flask import Blueprint, render_template, request, redirect
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
        weight = float(request.form.get("weight", 0)) / 100  # Convertir a decimal
        optional = bool(int(request.form.get("optional", 0)))

        current = sum(eval['weight'] for eval in service.get_all_evaluations_by_section(section_id))
        if current + weight > 1:
            error = "El peso total excede el 100%."
            evaluations = service.get_all_evaluations_by_section(section_id)
            return render_template("evaluations/index.html", section_id=section_id, evaluations=evaluations, error=error, total_weight=current * 100), HTTP_BAD_REQUEST

        service.add_evaluation(section_id, type_, weight, optional)
        return redirect(f"/sections/{section_id}/evaluations")
    except Exception as e:
        print("Error en create:", e)
        return "Error interno", 500

@evaluation_bp.route('/sections/<int:section_id>/evaluations/<int:eid>/delete', methods=['POST'])
def delete(section_id, eid):
    try:
        service.delete_evaluation(eid)
        return redirect(f"/sections/{section_id}/evaluations")
    except Exception as e:
        print("Error al eliminar evaluación:", e)
        return "Error interno", 500

@evaluation_bp.route('/sections/<int:section_id>/evaluations/<int:eid>/edit', methods=['POST'])
def update(section_id, eid):
    try:
        type_ = request.form.get("type", "").strip()
        weight = float(request.form.get("weight", 0)) / 100
        optional = bool(int(request.form.get("optional", 0)))

        all_evals = service.get_all_evaluations_by_section(section_id)
        current = sum(eval['weight'] for eval in all_evals if eval['id'] != eid)
        if current + weight > 1:
            error = "El peso total excede el 100%."
            evaluations = all_evals
            return render_template("evaluations/index.html", section_id=section_id, evaluations=evaluations, error=error, total_weight=(current + weight) * 100), HTTP_BAD_REQUEST

        service.update_evaluation(eid, type_, weight, optional)
        return redirect(f"/sections/{section_id}/evaluations")
    except Exception as e:
        print("Error en update:", e)
        return "Error interno", 500