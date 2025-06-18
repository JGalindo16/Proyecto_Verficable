from flask import Blueprint, render_template, request, redirect, flash
from app.services.course_service import CourseService
from app.settings import ALL_REGISTER_PAGE, CREATE_PAGE, REGISTER_PAGE
from app.http_errors import HTTP_BAD_REQUEST
from app.alertas.course_alerts import (
    CURSO_CREADO_EXITOSAMENTE,
    CURSO_ACTUALIZADO_EXITOSAMENTE,
    CURSO_ELIMINADO_EXITOSAMENTE,
    TODOS_LOS_CURSOS_ELIMINADOS,
    DATOS_CARGADOS_EXITOSAMENTE,
    CURSO_NO_ENCONTRADO,
    TODOS_LOS_CAMPOS_OBLIGATORIOS,
    CAMPOS_NO_PUEDEN_ESTAR_VACIOS,
    ARCHIVO_INVALIDO,
    ERROR_AL_CREAR_CURSO,
    ERROR_AL_ACTUALIZAR_CURSO,
    ERROR_AL_ELIMINAR_CURSO,
    ERROR_AL_ELIMINAR_TODOS,
    ERROR_AL_CARGAR_DATOS
)

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
        flash(CURSO_NO_ENCONTRADO, "danger")
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
        flash(CAMPOS_NO_PUEDEN_ESTAR_VACIOS, "danger")
        return render_template(CREATE_PAGE, form={"name": name, "code": code}), HTTP_BAD_REQUEST

    result = service.add_course(name, code)
    if not result["success"]:
        flash(result["message"] or ERROR_AL_CREAR_CURSO, "danger")
        return render_template(CREATE_PAGE, form={"name": name, "code": code}), HTTP_BAD_REQUEST

    flash(CURSO_CREADO_EXITOSAMENTE, "success")
    return redirect('/courses')

@course_bp.route('/courses/<int:id>/edit')
def edit_form(id):
    course = service.get_course_by_id(id)
    if not course:
        flash(CURSO_NO_ENCONTRADO, "danger")
        return redirect('/courses')
    return render_template('courses/edit.html', form=course)

@course_bp.route('/courses/<int:id>/edit', methods=['POST'])
def edit_course(id):
    name = request.form.get("name")
    code = request.form.get("code")

    if not name or not code:
        flash(TODOS_LOS_CAMPOS_OBLIGATORIOS, "danger")
        return render_template('courses/edit.html', form={"id": id, "name": name, "code": code}), HTTP_BAD_REQUEST

    result = service.update_course(id, name, code)
    if not result["success"]:
        flash(result["message"] or ERROR_AL_ACTUALIZAR_CURSO, "danger")
        return render_template('courses/edit.html', form={"id": id, "name": name, "code": code}), HTTP_BAD_REQUEST

    flash(CURSO_ACTUALIZADO_EXITOSAMENTE, "success")
    return redirect(f'/courses/{id}')

@course_bp.route('/courses/<int:id>/delete', methods=['POST'])
def delete_course(id):
    result = service.delete_course(id)
    if not result["success"]:
        flash(result["message"] or ERROR_AL_ELIMINAR_CURSO, "danger")
    else:
        flash(CURSO_ELIMINADO_EXITOSAMENTE, "success")
    return redirect('/courses')

@course_bp.route('/courses/delete-all', methods=['POST'])
def delete_all_courses():
    result = service.delete_all_courses()
    if not result["success"]:
        flash(result["message"] or ERROR_AL_ELIMINAR_TODOS, "danger")
    else:
        flash(TODOS_LOS_CURSOS_ELIMINADOS, "success")
    return redirect('/courses')

@course_bp.route('/load_json', methods=['POST'])
def load_json():
    file = request.files.get("fileInput")
    if not file or not file.filename.endswith(".json"):
        flash(ARCHIVO_INVALIDO, "danger")
        return render_template(CREATE_PAGE, form={"name": '', "code": ''}), HTTP_BAD_REQUEST

    result = service.process_json(file)
    if not result["success"]:
        flash(result["message"] or ERROR_AL_CARGAR_DATOS, "danger")
        return render_template(CREATE_PAGE, form={"name": '', "code": ''}), HTTP_BAD_REQUEST

    flash(DATOS_CARGADOS_EXITOSAMENTE, "success")
    return redirect('/courses')