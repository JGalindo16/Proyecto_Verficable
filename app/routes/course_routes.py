from flask import Blueprint, render_template, request, redirect
from app.services.course_service import CourseService
from app.settings import ALL_REGISTER_PAGE, CREATE_PAGE, JSON_FILE, REGISTER_PAGE
from app.http_errors import HTTP_BAD_REQUEST

course_bp = Blueprint('course', __name__)
service = CourseService()

@course_bp.route('/')
def index():
    return get_all()

@course_bp.route('/courses')
def get_all():
    courses = service.get_all_courses()
    return render_template(ALL_REGISTER_PAGE, data=courses)

@course_bp.route('/courses/<id>')
def get_by_id(id):
    course = service.get_course_by_id(id)
    return render_template(REGISTER_PAGE, data=course)

@course_bp.route('/create')
def create_form():
    return render_template(CREATE_PAGE, form={"textInput": '', "numInput": ''})

@course_bp.route('/courses', methods=['POST'])
def create_course():
    name = request.form["textInput"]
    code = request.form["numInput"]
    if len(name) == 0 or not code:
        return render_template(CREATE_PAGE, error="Los campos no pueden estar vacíos", form=request.form), HTTP_BAD_REQUEST
    service.add_course(name, code)
    return redirect('/courses')

@course_bp.route('/load_json', methods=['POST'])
def load_json():
    file = request.files["fileInput"]
    if not file.filename.endswith(".json"):
        return render_template(CREATE_PAGE, file_error="Archivo debe ser .json", form=request.form), HTTP_BAD_REQUEST
    service.process_json(file)
    return redirect('/courses')