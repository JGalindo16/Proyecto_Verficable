from flask import Blueprint, render_template, request, redirect, flash
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
        flash("Curso no encontrado.", "danger")
        return redirect('/courses')
    return render_template(REGISTER_PAGE, data=course)

@course_bp.route('/create')
def create_form():
    return render_template(CREATE_PAGE, form={"name": '', "code": ''})

@course_bp.route('/courses', methods=['POST'])
def create_course():
    name = request.form.get("name", "")
    code = request.form.get("code", "")

    if not name or not code:
        flash("Los campos no pueden estar vacíos.", "danger")
        return render_template(CREATE_PAGE, form={"name": name, "code": code}), HTTP_BAD_REQUEST

    result = service.add_course(name, code)
    if not result["success"]:
        flash(result["message"], "danger")
        return render_template(CREATE_PAGE, form={"name": name, "code": code}), HTTP_BAD_REQUEST

    flash("Curso creado exitosamente.", "success")
    return redirect('/courses')

@course_bp.route('/courses/<int:id>/edit')
def edit_form(id):
    course = service.get_course_by_id(id)
    if not course:
        flash("Curso no encontrado.", "danger")
        return redirect('/courses')
    return render_template('courses/edit.html', form=course)

@course_bp.route('/courses/<int:id>/edit', methods=['POST'])
def edit_course(id):
    name = request.form.get("name")
    code = request.form.get("code")

    if not name or not code:
        flash("Todos los campos son obligatorios.", "danger")
        return render_template('courses/edit.html', form={"id": id, "name": name, "code": code}), HTTP_BAD_REQUEST

    result = service.update_course(id, name, code)
    if not result["success"]:
        flash(result["message"], "danger")
        return render_template('courses/edit.html', form={"id": id, "name": name, "code": code}), HTTP_BAD_REQUEST

    flash("Curso actualizado correctamente.", "success")
    return redirect(f'/courses/{id}')

@course_bp.route('/courses/<int:id>/delete', methods=['POST'])
def delete_course(id):
    service.delete_course(id)
    flash("Curso eliminado correctamente.", "success")
    return redirect('/courses')

@course_bp.route('/load_json', methods=['POST'])
def load_json():
    file = request.files.get("fileInput")
    if not file or not file.filename.endswith(".json"):
        flash("El archivo debe tener extensión .json", "danger")
        return render_template(CREATE_PAGE, form={"name": '', "code": ''}), HTTP_BAD_REQUEST

    result = service.process_json(file)
    if not result["success"]:
        flash(result["message"], "danger")
        return render_template(CREATE_PAGE, form={"name": '', "code": ''}), HTTP_BAD_REQUEST

    flash("Datos cargados exitosamente.", "success")
    return redirect('/courses')