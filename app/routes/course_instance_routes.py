from flask import Blueprint, render_template, request, redirect
from app.services.course_instance_service import CourseInstanceService
from app.services.course_service import CourseService
from app.http_errors import HTTP_BAD_REQUEST

course_instance_bp = Blueprint('course_instance', __name__)
instance_service = CourseInstanceService()
course_service = CourseService()

@course_instance_bp.route('/courses/<int:course_id>/instances/create')
def create_instance_form(course_id):
    course = course_service.get_course_by_id(course_id)
    if not course:
        return "Curso no encontrado", 404
    return render_template('course_instances/create.html', form={"year": "", "semester": ""}, course=course)

@course_instance_bp.route('/courses/<int:course_id>/instances', methods=['POST'])
def create_instance(course_id):
    year = request.form.get("year")
    semester = request.form.get("semester")
    if not year or not semester:
        course = course_service.get_course_by_id(course_id)
        return render_template('course_instances/create.html', form=request.form, course=course, error="Todos los campos son obligatorios"), HTTP_BAD_REQUEST

    instance_service.add_instance(course_id, year, semester)
    return redirect(f'/courses/{course_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/delete', methods=['POST'])
def delete_instance(course_id, instance_id):
    instance_service.delete_instance(instance_id)
    return redirect(f'/courses/{course_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/edit', methods=['POST'])
def edit_instance(course_id, instance_id):
    year = request.form.get("year")
    semester = request.form.get("semester")
    if not year or not semester:
        course = course_service.get_course_by_id(course_id)
        return render_template('courses/show.html', data=course, error="Todos los campos son obligatorios")
    
    instance_service.update_instance(instance_id, year, semester)
    return redirect(f'/courses/{course_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>')
def view_instance(course_id, instance_id):
    instance = instance_service.get_instance_by_id(instance_id)
    course = course_service.get_course_by_id(course_id)
    professors = instance_service.get_all_professors()
    students = instance_service.get_all_students()
    
    if not instance or not course:
        return "Instancia o curso no encontrado", 404
    
    sections = instance_service.get_sections_by_instance(instance_id)
    
    for section in sections:
        section['enrolled_student_ids'] = instance_service.get_enrolled_student_ids(section['id'])

    return render_template(
        'course_instances/show.html',
        instance=instance,
        course=course,
        sections=sections,
        professors=professors,
        students=students
    )

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections', methods=['POST'])
def add_section(course_id, instance_id):
    section_name = request.form.get("section_name")
    professor_id = request.form.get("professor_id")
    student_ids = request.form.getlist("student_ids") 

    if not section_name or not professor_id:
        return redirect(f'/courses/{course_id}/instances/{instance_id}', code=400)

    section_id = instance_service.add_section(instance_id, section_name, professor_id)

    if student_ids:
        instance_service.add_students_to_section(section_id, student_ids)

    return redirect(f'/courses/{course_id}/instances/{instance_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/delete', methods=['POST'])
def delete_section(course_id, instance_id, section_id):
    instance_service.delete_section(section_id)
    return redirect(f'/courses/{course_id}/instances/{instance_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>')
def view_section(course_id, instance_id, section_id):
    course = course_service.get_course_by_id(course_id)
    instance = instance_service.get_instance_by_id(instance_id)
    section = instance_service.get_section_by_id(section_id)
    students = instance_service.get_students_in_section(section_id)
    professors = instance_service.get_all_professors()
    all_students = instance_service.get_all_students()
    enrolled_student_ids = instance_service.get_enrolled_student_ids(section_id)
    
    if not course or not instance or not section:
        return "Recurso no encontrado", 404
        
    return render_template(
        'sections/show.html',
        course=course,
        instance=instance,
        section=section,
        students=students,
        professors=professors,
        all_students=all_students,
        enrolled_student_ids=enrolled_student_ids
    )

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/edit', methods=['POST'])
def update_section(course_id, instance_id, section_id):
    section_number = request.form.get('section_number')
    professor_id = request.form.get('professor_id')
    student_ids = request.form.getlist('student_ids')
    
    if not section_number or not professor_id:
        return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')
    
    success = instance_service.update_section(section_id, section_number, professor_id)
    
    if success:
        instance_service.update_section_students(section_id, student_ids)
    
    return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/grades')
def view_course_grades(course_id, instance_id):
    course_info = instance_service.get_course_info_for_grades(course_id, instance_id)
    if not course_info:
        return "Curso o instancia no encontrada", 404
    
    grades_data = instance_service.get_course_grades(course_id, instance_id)
    
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
        section_number = grade['section_number']
        
        if evaluation_type not in evaluation_weights:
            evaluation_weights[evaluation_type] = evaluation_weight
        evaluation_types.add(evaluation_type)
        
        if student_id not in students_data:
            students_data[student_id] = {
                'name': student_name,
                'section': section_number,
                'evaluations': {},
                'type_averages': {},
                'final_average': 0
            }
        
        if evaluation_type not in students_data[student_id]['evaluations']:
            students_data[student_id]['evaluations'][evaluation_type] = []
        
        students_data[student_id]['evaluations'][evaluation_type].append({
            'name': evaluation_name,
            'specific_weight': specific_weight,
            'score': score
        })
    
    for student_id, student in students_data.items():
        final_score = 0
        
        for eval_type, evals in student['evaluations'].items():
            type_total = 0
            weight_sum = 0
            
            for eval_item in evals:
                type_total += eval_item['score'] * eval_item['specific_weight']
                weight_sum += eval_item['specific_weight']
            
            if weight_sum > 0:
                type_avg = type_total / weight_sum
            else:
                type_avg = 0
                
            student['type_averages'][eval_type] = round(type_avg, 1)
            final_score += type_avg * evaluation_weights[eval_type]
        
        student['final_average'] = round(final_score, 1)
    
    return render_template(
        'grades/course_grades.html',
        course_info=course_info,
        students_data=students_data,
        evaluation_types=sorted(list(evaluation_types)),
        evaluation_weights=evaluation_weights,
        course_id=course_id,
        instance_id=instance_id
    )

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/grades')
def view_section_grades(course_id, instance_id, section_id):
    course = course_service.get_course_by_id(course_id)
    instance = instance_service.get_instance_by_id(instance_id)
    section = instance_service.get_section_by_id(section_id)
    
    if not course or not instance or not section:
        return "Recurso no encontrado", 404
    
    grades_data = instance_service.get_section_grades(section_id)
    
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
    
    for student_id, student in students_data.items():
        final_score = 0
        
        for eval_type, evals in student['evaluations'].items():
            type_total = 0
            weight_sum = 0
            
            for eval_item in evals:
                if eval_item['score'] is not None:
                    type_total += eval_item['score'] * eval_item['specific_weight']
                    weight_sum += eval_item['specific_weight']
            
            if weight_sum > 0:
                type_avg = type_total / weight_sum
            else:
                type_avg = 0
                
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

@course_instance_bp.route('/grades/update', methods=['POST'])
def update_grade():
    from app.services.course_instance_service import CourseInstanceService
    service = CourseInstanceService()

    data = request.json
    print("DEBUG /grades/update:", data)
    section_id = data.get('section_id')
    student_id = data.get('student_id')
    instance_eval_id = data.get('instance_eval_id')
    score = data.get('score')

    if section_id is None or student_id is None or instance_eval_id is None or score is None:
        return {"success": False, "message": "Faltan parámetros"}, 400

    try:
        score = float(score)
    except (ValueError, TypeError):
        return {"success": False, "message": "Score inválido"}, 400

    success, type_avg, final_avg = service.create_or_update_grade(
        int(section_id), int(student_id), int(instance_eval_id), score
    )

    return {
        "success": success,
        "type_average": type_avg,
        "final_average": final_avg
    }, 200 if success else 500
