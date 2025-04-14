from flask import Blueprint, render_template, request, redirect
from app.services.course_service import CourseService
from app.settings import ALL_REGISTER_PAGE, CREATE_PAGE, REGISTER_PAGE
from app.http_errors import HTTP_BAD_REQUEST

course_bp = Blueprint('course', __name__)
service = CourseService()

@course_bp.route('/')
def home():
    return render_template('global/home.html')

@course_bp.route('/courses')
def get_all():
    courses = service.get_all_courses()
    return render_template(ALL_REGISTER_PAGE, data=courses)

@course_bp.route('/courses/<int:id>')
def get_by_id(id):
    course = service.get_course_by_id(id)
    if not course:
        return "Curso no encontrado", 404
    return render_template(REGISTER_PAGE, data=course)

@course_bp.route('/create')
def create_form():
    return render_template(CREATE_PAGE, form={"name": '', "code": ''})

@course_bp.route('/courses', methods=['POST'])
def create_course():
    name = request.form.get("name", "")
    code = request.form.get("code", "")
    if not name or not code:
        return render_template(CREATE_PAGE, error="Los campos no pueden estar vacíos", form={"name": name, "code": code}), HTTP_BAD_REQUEST
    service.add_course(name, code)
    return redirect('/courses')

@course_bp.route('/courses/<int:id>/edit')
def edit_form(id):
    course = service.get_course_by_id(id)
    if not course:
        return "Curso no encontrado", 404
    return render_template('courses/edit.html', form=course)

@course_bp.route('/courses/<int:id>/edit', methods=['POST'])
def edit_course(id):
    name = request.form.get("name")
    code = request.form.get("code")
    if not name or not code:
        return render_template('courses/edit.html', form={"id": id, "name": name, "code": code}, error="Todos los campos son obligatorios"), HTTP_BAD_REQUEST
    service.update_course(id, name, code)
    return redirect(f'/courses/{id}')

@course_bp.route('/courses/<int:id>/delete', methods=['POST'])
def delete_course(id):
    service.delete_course(id)
    return redirect('/courses')

@course_bp.route('/load_json', methods=['POST'])
def load_json():
    file = request.files["fileInput"]
    if not file.filename.endswith(".json"):
        return render_template(CREATE_PAGE, file_error="El archivo debe tener extensión .json", form={"name": '', "code": ''}), HTTP_BAD_REQUEST
    service.process_json(file)
    return redirect('/courses')