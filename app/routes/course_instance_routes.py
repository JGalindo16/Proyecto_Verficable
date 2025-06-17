from flask import Blueprint, render_template, request, redirect, flash
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
        flash("Curso no encontrado.", "error")
        return redirect('/')
    return render_template('course_instances/show.html', form={"year": "", "semester": ""}, course=course)

@course_instance_bp.route('/courses/<int:course_id>/instances', methods=['POST'])
def create_instance(course_id):
    year = request.form.get("year")
    semester = request.form.get("semester")
    
    if not year or not semester:
        course = course_service.get_course_by_id(course_id)
        flash("Todos los campos son obligatorios.", "danger")
        return render_template('courses/show.html', data=course), HTTP_BAD_REQUEST

    result = instance_service.add_instance(course_id, year, semester)
    
    if not result["success"]:
        flash(result["message"], "danger")
    else:
        flash("Instancia creada exitosamente.", "success")

    return redirect(f'/courses/{course_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/delete', methods=['POST'])
def delete_instance(course_id, instance_id):
    status = instance_service.delete_instance(instance_id)
    if status != 200:
        flash("No se pudo eliminar la instancia.", "error")
    else:
        flash("Instancia eliminada correctamente.", "success")
    return redirect(f'/courses/{course_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/edit', methods=['POST'])
def edit_instance(course_id, instance_id):
    year = request.form.get("year")
    semester = request.form.get("semester")
    
    if not year or not semester:
        course = course_service.get_course_by_id(course_id)
        flash("Todos los campos son obligatorios.", "danger")
        return render_template('courses/show.html', data=course), HTTP_BAD_REQUEST

    result = instance_service.update_instance(instance_id, year, semester)
    
    if not result["success"]:
        flash(result["message"], "danger")
    else:
        flash("Instancia actualizada correctamente.", "success")
    
    return redirect(f'/courses/{course_id}')

@course_instance_bp.route('/courses/<int:course_id>/instances/<int:instance_id>')
def view_instance(course_id, instance_id):
    from app.services.section_service import SectionService
    section_service = SectionService()

    instance = instance_service.get_instance_by_id(instance_id)
    course = course_service.get_course_by_id(course_id)
    professors = section_service.get_all_professors()
    students = section_service.get_all_students()

    if not instance or not course:
        flash("Instancia o curso no encontrado.", "error")
        return redirect('/')

    sections = section_service.get_sections_by_instance(instance_id)
    for section in sections:
        section['enrolled_student_ids'] = section_service.get_enrolled_student_ids(section['id'])

    return render_template(
        'course_instances/show.html',
        instance=instance,
        course=course,
        sections=sections,
        professors=professors,
        students=students
    )