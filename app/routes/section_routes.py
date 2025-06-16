from flask import Blueprint, render_template, request, redirect
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
    student_ids = request.form.getlist("student_ids") 

    if not section_name or not professor_id:
        return redirect(f'/courses/{course_id}/instances/{instance_id}', code=400)

    section_id = section_service.add_section(instance_id, section_name, professor_id)

    if student_ids:
        section_service.add_students_to_section(section_id, student_ids)

    return redirect(f'/courses/{course_id}/instances/{instance_id}')

@section_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/delete', methods=['POST'])
def delete_section(course_id, instance_id, section_id):
    section_service.delete_section(section_id)
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

@section_bp.route('/courses/<int:course_id>/instances/<int:instance_id>/sections/<int:section_id>/edit', methods=['POST'])
def update_section(course_id, instance_id, section_id):
    section_number = request.form.get('section_number')
    professor_id = request.form.get('professor_id')
    student_ids = request.form.getlist('student_ids')
    
    if not section_number or not professor_id:
        return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')
    
    success = section_service.update_section(section_id, section_number, professor_id)
    
    if success:
        section_service.update_section_students(section_id, student_ids)
    
    return redirect(f'/courses/{course_id}/instances/{instance_id}/sections/{section_id}')
