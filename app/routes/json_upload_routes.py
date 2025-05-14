from flask import Blueprint, render_template, request
from app.services.json_upload_service import JsonUploadService
from flask import flash, redirect, url_for

json_upload_bp = Blueprint('json_upload', __name__)
service = JsonUploadService()

@json_upload_bp.route('/json-upload/alumnos', methods=['GET', 'POST'])
def upload_alumnos():
    message = None
    success = False

    if request.method == 'POST':
        file = request.files.get('json_file')
        if not file:
            message = "Debe subir un archivo."
        else:
            success, message = service.load_alumnos(file)

    
    flash(message, 'success' if success else 'danger')
    return redirect('/')

@json_upload_bp.route('/json-upload/profesores', methods=['POST'])
def upload_profesores():
    message = None
    success = False

    file = request.files.get('json_file')
    if not file:
        message = "Debe subir un archivo."
    else:
        success, message = service.load_profesores(file)

    flash(message, 'success' if success else 'danger')
    return redirect('/')

@json_upload_bp.route('/json-upload/cursos', methods=['POST'])
def upload_cursos():
    file = request.files.get('json_file')
    success, message = service.load_cursos(file) if file else (False, "Debe subir un archivo.")
    flash(message, 'success' if success else 'danger')
    return redirect('/')

@json_upload_bp.route('/json-upload/instancias', methods=['POST'])
def upload_instancias():
    message = None
    success = False

    file = request.files.get('json_file')
    if not file:
        message = "Debe subir un archivo."
    else:
        success, message = service.load_instancias(file)

    flash(message, 'success' if success else 'danger')
    return redirect('/')

@json_upload_bp.route('/json-upload/inscripciones', methods=['POST'])
def upload_inscripciones():
    file = request.files.get('json_file')
    if not file:
        flash("Debe subir un archivo.", "danger")
        return redirect(url_for('home'))

    success, message = service.load_enrollments(file)
    flash(message, 'success' if success else 'danger')
    return redirect('/')

@json_upload_bp.route('/json-upload/salas', methods=['POST'])
def upload_classrooms():
    success = False
    message = None

    file = request.files.get('json_file')
    if not file:
        message = "Debe subir un archivo."
    else:
        success, message = service.load_classrooms(file)

    flash(message, 'success' if success else 'danger')
    return redirect('/')