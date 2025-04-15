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