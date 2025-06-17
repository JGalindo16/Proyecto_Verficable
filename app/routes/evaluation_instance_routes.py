from flask import Blueprint, render_template, request, redirect
from app.services.evaluation_instance_service import EvaluationInstanceService
from app.http_errors import HTTP_BAD_REQUEST

instance_bp = Blueprint('instance', __name__)
service = EvaluationInstanceService()

@instance_bp.route('/evaluations/<int:evaluation_id>/instances')
def index(evaluation_id):
    instances = service.get_instances_by_evaluation(evaluation_id)
    total_weight = service.get_total_specific_weight_by_evaluation(evaluation_id)
    return render_template('evaluation_instances/index.html', instances=instances, evaluation_id=evaluation_id, total_weight=total_weight)

@instance_bp.route('/evaluations/<int:evaluation_id>/instances', methods=['POST'])
def create(evaluation_id):
    try:
        name = request.form.get("name", "").strip()
        specific_weight = float(request.form.get("specific_weight", 0)) / 100 
        mandatory = bool(int(request.form.get("mandatory", 0)))

        current = service.get_total_specific_weight_by_evaluation(evaluation_id)
        if current + specific_weight > 1:
            error = "El peso total de las instancias excede el 100%."
            instances = service.get_instances_by_evaluation(evaluation_id)
            return render_template("evaluation_instances/index.html", evaluation_id=evaluation_id, instances=instances, error=error, total_weight=current * 100), HTTP_BAD_REQUEST

        service.add_instance(evaluation_id, name, specific_weight, mandatory)
        return redirect(f"/evaluations/{evaluation_id}/instances")
    except Exception as e:
        print("Error en create:", e)
        return "Error interno", 500

@instance_bp.route('/evaluations/<int:evaluation_id>/instances/<int:instance_id>/edit', methods=['POST'])
def update(evaluation_id, instance_id):
    try:
        name = request.form.get("name", "").strip()
        specific_weight = float(request.form.get("specific_weight", 0)) / 100
        mandatory = bool(int(request.form.get("mandatory", 0)))

        current = service.get_total_specific_weight_by_evaluation(evaluation_id, exclude_instance_id=instance_id)
        if current + specific_weight > 1:
            error = "El peso total de las instancias excede el 100%."
            instances = service.get_instances_by_evaluation(evaluation_id)
            return render_template("evaluation_instances/index.html", evaluation_id=evaluation_id, instances=instances, error=error, total_weight=(current + specific_weight) * 100), HTTP_BAD_REQUEST

        service.update_instance(instance_id, name, specific_weight, mandatory)
        return redirect(f"/evaluations/{evaluation_id}/instances")
    except Exception as e:
        print("Error en update:", e)
        return "Error interno", 500

@instance_bp.route('/evaluations/<int:evaluation_id>/instances/<int:instance_id>/delete', methods=['POST'])
def delete(evaluation_id, instance_id):
    try:
        service.delete_instance(instance_id)
        return redirect(f"/evaluations/{evaluation_id}/instances")
    except Exception as e:
        print("Error en delete:", e)
        return "Error interno", 500