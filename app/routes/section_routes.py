from flask import Blueprint, render_template, request, redirect, flash
from app.services.section_service import SectionService
from app.services.course_instance_service import CourseInstanceService
from app.services.course_service import CourseService
from app.http_errors import HTTP_BAD_REQUEST

section_bp = Blueprint('section', __name__)
section_service = SectionService()
instance_service = CourseInstanceService()
course_service = CourseService()

@section_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections', methods=['POST'])
def add_section(course_id, instance_id):
    section_name = request.form.get("section_name")
    professor_id = request.form.get("professor_id")
    student_ids = request.form.getlist("student_ids") or []

    if not section_name or not professor_id:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(f'/courses/{course_id}/instances/{instance_id}')

    for student_id in student_ids:
        result = section_service.check_student_enrollment_in_instance(student_id, instance_id)
        if result:
            flash(f"El estudiante \"{result['name']}\" ya está inscrito en otra sección de esta instancia.", "danger")
            return redirect(f'/courses/{course_id}/instances/{instance_id}')

    result = section_service.add_section(instance_id, section_name, professor_id, student_ids)

    if not result["success"]:
        flash(result["message"], "danger")
        return redirect(f'/courses/{course_id}/instances/{instance_id}')

    flash("Sección creada exitosamente.", "success")
    return redirect(f'/courses/{course_id}/instances/{instance_id}')

@section_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/delete', methods=['POST'])
def delete_section(course_id, instance_id, section_id):
    result = section_service.delete_section(section_id)
    if not result["success"]:
        flash(result["message"], "danger")
    else:
        flash("Sección eliminada exitosamente.", "success")
    return redirect(f'/courses/{course_id}/instances/{instance_id}')

@section_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>')
def view_section(course_id, instance_id, section_id):
    course = course_service.get_course_by_id(course_id)
    instance = instance_service.get_instance_by_id(instance_id)
    section = section_service.get_section_by_id(section_id)
    students = section_service.get_students_in_section(section_id)
    professors = section_service.get_all_professors()
    all_students = section_service.get_all_students()
    enrolled_student_ids = section_service.get_enrolled_student_ids(section_id)

    if not course or not instance or not section:
        flash("Recurso no encontrado.", "danger")
        return redirect(f'/courses/{course_id}/instances/{instance_id}')

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

@section_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/edit', methods=['POST'])
def update_section(course_id, instance_id, section_id):
    section_number = request.form.get('section_number')
    professor_id = request.form.get('professor_id')
    student_ids = request.form.getlist('student_ids')

    if not section_number or not professor_id:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')

    for student_id in student_ids:
        result = section_service.check_student_enrollment_in_instance(student_id, instance_id, section_id)
        if result:
            flash(f"El estudiante \"{result['name']}\" ya está inscrito en otra sección de esta instancia.", "danger")
            return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')

    result = section_service.update_section(section_id, section_number, professor_id)
    if not result["success"]:
        flash(result["message"], "danger")
        return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')

    section_service.update_section_students(section_id, student_ids)
    flash("Sección actualizada exitosamente.", "success")
    return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')
