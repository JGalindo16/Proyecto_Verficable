from flask import Blueprint, render_template, request, jsonify
from app.services.grade_service import GradeService
from app.utils.grades_utils import (
    validate_and_get_entities,
    process_grades_data
)

grade_bp = Blueprint('grade', __name__)
grade_service = GradeService()

@grade_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/grades')
def view_section_grades(course_id, instance_id, section_id):
    entities = validate_and_get_entities(course_id, instance_id, section_id)
    if not entities:
        return "Recurso no encontrado", 404

    course, instance, section = entities
    processed_data = process_grades_data(section_id)

    return render_template(
        'grades/section_grades.html',
        course=course,
        instance=instance,
        section=section,
        **processed_data
    )

@grade_bp.route('/grades/update', methods=['POST'])
def update_grade():
    data = request.json
    section_id = data.get('section_id')
    student_id = data.get('student_id')
    instance_eval_id = data.get('instance_eval_id')
    score = data.get('score')

    if not all([section_id, student_id, instance_eval_id, score]):
        return jsonify({"success": False, "message": "Faltan parámetros"}), 400

    try:
        score = float(score)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Score inválido"}), 400

    result = grade_service.create_or_update_grade(
        int(section_id), int(student_id), int(instance_eval_id), score
    )

    if result["success"]:
        return jsonify({
            "success": True,
            "type_average": result["type_average"],
            "final_average": result["final_average"]
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Error al guardar la nota"
        }), 500