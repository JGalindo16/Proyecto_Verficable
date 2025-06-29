from flask import flash
from app.services.grade_service import GradeService
from app.services.course_service import CourseService
from app.services.course_instance_service import CourseInstanceService
from app.services.section_service import SectionService

grade_service = GradeService()
course_service = CourseService()
instance_service = CourseInstanceService()
section_service = SectionService()


def validate_and_get_entities(course_id, instance_id, section_id):
    course = course_service.get_course_by_id(course_id)
    instance = instance_service.get_instance_by_id(instance_id)
    section = section_service.get_section_by_id(section_id)

    if not course or not instance or not section:
        flash("Recurso no encontrado.", "danger")
        return None

    return course, instance, section


def process_grades_data(section_id):
    grades_data = grade_service.get_section_grades(section_id)
    students_data = build_students_structure(grades_data)
    evaluation_types, evaluation_weights = extract_evaluation_info(grades_data)
    calculate_student_averages(students_data, evaluation_weights)

    return {
        'students_data': students_data,
        'evaluation_types': sorted(list(evaluation_types)),
        'evaluation_weights': evaluation_weights
    }


def build_students_structure(grades_data):
    students_data = {}

    for grade in grades_data:
        student_id = grade['student_id']
        student_name = grade['student_name']
        evaluation_type = grade['evaluation_type']
        evaluation_name = grade['evaluation_name']
        specific_weight = grade['specific_weight']
        score = grade['score']
        instance_eval_id = grade['instance_eval_id']

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

    return students_data


def extract_evaluation_info(grades_data):
    evaluation_types = set()
    evaluation_weights = {}

    for grade in grades_data:
        evaluation_type = grade['evaluation_type']
        evaluation_weight = grade['evaluation_weight']

        if evaluation_type not in evaluation_weights:
            evaluation_weights[evaluation_type] = evaluation_weight
        evaluation_types.add(evaluation_type)

    return evaluation_types, evaluation_weights


def calculate_student_averages(students_data, evaluation_weights):
    for student in students_data.values():
        final_score = 0
        for eval_type, evals in student['evaluations'].items():
            type_avg = calculate_type_average(evals)
            student['type_averages'][eval_type] = type_avg
            final_score += type_avg * evaluation_weights[eval_type]
        student['final_average'] = round(final_score, 1)


def calculate_type_average(evaluations):
    type_total = 0
    weight_sum = 0
    for eval_item in evaluations:
        if eval_item['score'] is not None:
            type_total += eval_item['score'] * eval_item['specific_weight']
            weight_sum += eval_item['specific_weight']
    return round(type_total / weight_sum, 1) if weight_sum > 0 else 0