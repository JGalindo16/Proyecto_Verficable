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
    sections = instance_service.get_sections_by_instance(instance_id)
    professors = instance_service.get_all_professors()
    students = instance_service.get_all_students()

    if not instance or not course:
        return "Instancia o curso no encontrado", 404

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
    student_ids = request.form.getlist("student_ids")  # Lista de IDs de estudiantes seleccionados

    if not section_name or not professor_id:
        # Redirigir con un mensaje de error si faltan datos
        return redirect(f'/courses/{course_id}/instances/{instance_id}', code=400)

    # Crear la sección
    section_id = instance_service.add_section(instance_id, section_name, professor_id)

    # Asignar estudiantes a la sección
    if student_ids:
        instance_service.add_students_to_section(section_id, student_ids)

    # Redirigir de vuelta a la página de la instancia
    return redirect(f'/courses/{course_id}/instances/{instance_id}')