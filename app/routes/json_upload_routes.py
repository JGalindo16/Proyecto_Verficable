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