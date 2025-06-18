from flask import Blueprint, request, jsonify
from app.services.json_upload_service import JsonUploadService

json_upload_bp = Blueprint('json_upload', __name__)
service = JsonUploadService()

@json_upload_bp.route('/json-upload/alumnos', methods=['POST'])
def upload_alumnos():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_alumnos(file)
    return jsonify(success=success, message=message)


@json_upload_bp.route('/json-upload/profesores', methods=['POST'])
def upload_profesores():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_profesores(file)
    return jsonify(success=success, message=message)


@json_upload_bp.route('/json-upload/cursos', methods=['POST'])
def upload_cursos():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_cursos(file)
    return jsonify(success=success, message=message)


@json_upload_bp.route('/json-upload/instancias', methods=['POST'])
def upload_instancias():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_instancias(file)
    return jsonify(success=success, message=message)


@json_upload_bp.route('/json-upload/inscripciones', methods=['POST'])
def upload_inscripciones():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_enrollments(file)
    return jsonify(success=success, message=message)


@json_upload_bp.route('/json-upload/salas', methods=['POST'])
def upload_classrooms():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_classrooms(file)
    return jsonify(success=success, message=message)


@json_upload_bp.route('/json-upload/instancias-secciones', methods=['POST'])
def upload_instancias_y_secciones():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_instancias_con_secciones(file)
    return jsonify(success=success, message=message)

@json_upload_bp.route('/json-upload/notas', methods=['POST'])
def upload_notas():
    file = request.files.get('json_file')
    if not file:
        return jsonify(success=False, message="Debe subir un archivo."), 400

    success, message = service.load_notas(file)
    status_code = 200 if success else 400
    return jsonify(success=success, message=message), status_code
