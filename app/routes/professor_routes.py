from flask import Blueprint, render_template, request, redirect
from app.services.professor_service import ProfessorService
from app.http_errors import HTTP_BAD_REQUEST

professor_bp = Blueprint('professor', __name__)
service = ProfessorService()

@professor_bp.route('/professors')
def get_all_professors():
    professors = service.get_all_professors()
    return render_template('professors/index.html', data=professors)

@professor_bp.route('/professors/<int:id>')
def get_professor(id):
    professor = service.get_professor_by_id(id)
    if not professor:
        return "Profesor no encontrado", 404
    return render_template('professors/show.html', data=professor)

@professor_bp.route('/professors/create')
def create_professor_form():
    return render_template('professors/create.html', form={"name": "", "email": ""})

@professor_bp.route('/professors', methods=['POST'])
def create_professor():
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    if not name or not email:
        return render_template('professors/create.html', error="Todos los campos son obligatorios", form={"name": name, "email": email}), HTTP_BAD_REQUEST
    service.add_professor(name, email)
    return redirect('/professors')

@professor_bp.route('/professors/<int:id>/edit')
def edit_professor_form(id):
    professor = service.get_professor_by_id(id)
    if not professor:
        return "Profesor no encontrado", 404
    return render_template('professors/edit.html', form=professor)

@professor_bp.route('/professors/<int:id>/edit', methods=['POST'])
def edit_professor(id):
    name = request.form.get("name")
    email = request.form.get("email")
    if not name or not email:
        return render_template('professors/edit.html', form={"id": id, "name": name, "email": email}, error="Todos los campos son obligatorios"), HTTP_BAD_REQUEST
    service.update_professor(id, name, email)
    return redirect(f'/professors/{id}')

@professor_bp.route('/professors/<int:id>/delete', methods=['POST'])
def delete_professor(id):
    service.delete_professor(id)
    return redirect('/professors')