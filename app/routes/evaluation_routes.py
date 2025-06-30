from flask import Blueprint, render_template, request, redirect, flash
from app.services.evaluation_service import EvaluationService

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
        evaluation_data = extract_evaluation_data()
        
        validation_error = validate_evaluation_data(evaluation_data, section_id)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(f"/sections/{section_id}/evaluations")
        
        result = service.add_evaluation(section_id, evaluation_data['type'], evaluation_data['weight'], evaluation_data['optional'])
        return handle_service_result(result, section_id, "creada")
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
        evaluation_data = extract_evaluation_data()
        
        validation_error = validate_evaluation_update(evaluation_data, section_id, eid)
        if validation_error:
            flash(validation_error, "danger")
            return redirect(f"/sections/{section_id}/evaluations")
        
        result = service.update_evaluation(eid, evaluation_data['type'], evaluation_data['weight'], evaluation_data['optional'])
        return handle_service_result(result, section_id, "actualizada")
    except Exception as e:
        print("Error en update:", e)
        flash("Error interno al actualizar evaluación.", "danger")
        return redirect(f"/sections/{section_id}/evaluations")

def extract_evaluation_data():
    return {
        'type': request.form.get("type", "").strip(),
        'weight': float(request.form.get("weight", 0)) / 100,
        'optional': bool(int(request.form.get("optional", 0)))
    }

def validate_evaluation_data(evaluation_data, section_id):
    if not evaluation_data['type']:
        return "El tipo de evaluación es obligatorio."
    
    current_weight = service.get_total_weight_by_section(section_id)
    if current_weight + evaluation_data['weight'] > 1.0:
        return "El peso total excede el 100%."
    
    return None

def validate_evaluation_update(evaluation_data, section_id, eid):
    if not evaluation_data['type']:
        return "El tipo de evaluación es obligatorio."
    
    evaluations = service.get_all_evaluations_by_section(section_id)
    current_weight = sum(e['weight'] for e in evaluations if e['id'] != eid)
    if current_weight + evaluation_data['weight'] > 1.0:
        return "El peso total excede el 100%."
    
    return None

def handle_service_result(result, section_id, action):
    if not result["success"]:
        flash(result.get("message", f"Error al {action} la evaluación."), "danger")
    else:
        flash(f"Evaluación {action} exitosamente.", "success")
    return redirect(f"/sections/{section_id}/evaluations")
