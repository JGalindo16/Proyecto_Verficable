from flask import Blueprint, render_template, request, jsonify, flash
from app.services.grade_service import GradeService
from app.services.course_service import CourseService
from app.services.course_instance_service import CourseInstanceService
from app.services.section_service import SectionService

grade_bp = Blueprint('grade', __name__)
grade_service = GradeService()
course_service = CourseService()
instance_service = CourseInstanceService()
section_service = SectionService()

@grade_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/grades')
def view_section_grades(course_id, instance_id, section_id):
    course = course_service.get_course_by_id(course_id)
    instance = instance_service.get_instance_by_id(instance_id)
    section = section_service.get_section_by_id(section_id)

    if not course or not instance or not section:
        flash("Recurso no encontrado.", "danger")
        return "Recurso no encontrado", 404

    grades_data = grade_service.get_section_grades(section_id)
    
    students_data = {}
    evaluation_types = set()
    evaluation_weights = {}

    for grade in grades_data:
        student_id = grade['student_id']
        student_name = grade['student_name']
        evaluation_type = grade['evaluation_type']
        evaluation_weight = grade['evaluation_weight']
        evaluation_name = grade['evaluation_name']
        specific_weight = grade['specific_weight']
        score = grade['score']
        instance_eval_id = grade['instance_eval_id']

        if evaluation_type not in evaluation_weights:
            evaluation_weights[evaluation_type] = evaluation_weight
        evaluation_types.add(evaluation_type)

        if student_id not in students_data:
            students_data[student_id] = {
                'name': student_name,
                'evaluations': {},
                'type_averages': {},
                'final_average': 0
            }

        if evaluation_type not in students_data[student_id]['evaluations']:
            students_data[student_id]['evaluations'][evaluation_type] = []

        students_data[student_id]['evaluations'][evaluation_type].append({
            'name': evaluation_name,
            'specific_weight': specific_weight,
            'score': score,
            'instance_eval_id': instance_eval_id
        })

    # Calcular promedios por tipo y final
    for student_id, student in students_data.items():
        final_score = 0
        for eval_type, evals in student['evaluations'].items():
            type_total = 0
            weight_sum = 0
            for eval_item in evals:
                if eval_item['score'] is not None:
                    type_total += eval_item['score'] * eval_item['specific_weight']
                    weight_sum += eval_item['specific_weight']
            type_avg = type_total / weight_sum if weight_sum > 0 else 0
            student['type_averages'][eval_type] = round(type_avg, 1)
            final_score += type_avg * evaluation_weights[eval_type]
        student['final_average'] = round(final_score, 1)

    return render_template(
        'grades/section_grades.html',
        course=course,
        instance=instance,
        section=section,
        students_data=students_data,
        evaluation_types=sorted(list(evaluation_types)),
        evaluation_weights=evaluation_weights
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