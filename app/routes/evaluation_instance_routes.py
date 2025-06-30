from flask import Blueprint, render_template, request, redirect, flash
from app.services.evaluation_instance_service import EvaluationInstanceService

instance_bp = Blueprint('instance', __name__)
service = EvaluationInstanceService()

@instance_bp.route('/evaluations/<int:evaluation_id>/instances')
def index(evaluation_id):
    instances = service.get_instances_by_evaluation(evaluation_id)
    total_weight = service.get_total_specific_weight_by_evaluation(evaluation_id)
    return render_template(
        'evaluation_instances/index.html',
        instances=instances,
        evaluation_id=evaluation_id,
        total_weight=total_weight * 100
    )

@instance_bp.route('/evaluations/<int:evaluation_id>/instances', methods=['POST'])
def create(evaluation_id):
    try:
        name = request.form.get("name", "").strip()
        specific_weight = float(request.form.get("specific_weight", 0)) / 100
        mandatory = bool(int(request.form.get("mandatory", 0)))

        if not name:
            flash("El nombre de la instancia es obligatorio.", "danger")
            return redirect(f"/evaluations/{evaluation_id}/instances")

        current = service.get_total_specific_weight_by_evaluation(evaluation_id)
        if current + specific_weight > 1.01:
            flash("El peso total de las instancias excede el 100%.", "danger")
            return redirect(f"/evaluations/{evaluation_id}/instances")

        status = service.add_instance(evaluation_id, name, specific_weight, mandatory)
        if not status["success"]:
            flash(status.get("message", "Error al agregar la instancia."), "danger")
        else:
            flash("Instancia agregada exitosamente.", "success")
        return redirect(f"/evaluations/{evaluation_id}/instances")
    except Exception as e:
        print("Error en create:", e)
        flash("Error inesperado al crear la instancia.", "danger")
        return redirect(f"/evaluations/{evaluation_id}/instances")

@instance_bp.route('/evaluations/<int:evaluation_id>/instances/<int:instance_id>/edit', methods=['POST'])
def update(evaluation_id, instance_id):
    try:
        name = request.form.get("name", "").strip()
        specific_weight = float(request.form.get("specific_weight", 0)) / 100
        mandatory = bool(int(request.form.get("mandatory", 0)))

        if not name:
            flash("El nombre de la instancia es obligatorio.", "danger")
            return redirect(f"/evaluations/{evaluation_id}/instances")

        current = service.get_total_specific_weight_by_evaluation(evaluation_id, exclude_instance_id=instance_id)
        if current + specific_weight > 1.01:
            flash("El peso total de las instancias excede el 100%.", "danger")
            return redirect(f"/evaluations/{evaluation_id}/instances")

        status = service.update_instance(evaluation_id, instance_id, name, specific_weight, mandatory)
        if not status["success"]:
            flash(status["message"], "danger")
        else:
            flash("Instancia actualizada correctamente.", "success")

        return redirect(f"/evaluations/{evaluation_id}/instances")

    except Exception as e:
        print("Error en update:", e)
        flash("Error inesperado al actualizar la instancia.", "danger")
        return redirect(f"/evaluations/{evaluation_id}/instances")

@instance_bp.route('/evaluations/<int:evaluation_id>/instances/<int:instance_id>/delete', methods=['POST'])
def delete(evaluation_id, instance_id):
    try:
        status = service.delete_instance(instance_id)
        if status != 200:
            flash("Error al eliminar la instancia.", "danger")
        else:
            flash("Instancia eliminada exitosamente.", "success")
        return redirect(f"/evaluations/{evaluation_id}/instances")
    except Exception as e:
        print("Error en delete:", e)
        flash("Error inesperado al eliminar la instancia.", "danger")
        return redirect(f"/evaluations/{evaluation_id}/instances")
