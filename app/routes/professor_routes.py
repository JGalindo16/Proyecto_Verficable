from flask import Blueprint, render_template, request, redirect, flash
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
        flash("Profesor no encontrado.", "danger")
        return redirect('/professors')
    return render_template('professors/show.html', data=professor)

@professor_bp.route('/professors/create')
def create_professor_form():
    return render_template('professors/create.html', form={"name": "", "email": ""})

@professor_bp.route('/professors', methods=['POST'])
def create_professor():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if not name or not email:
        flash("Todos los campos son obligatorios.", "danger")
        return render_template('professors/create.html', form={"name": name, "email": email}), HTTP_BAD_REQUEST

    result = service.add_professor(name, email)
    if not result["success"]:
        flash(result["message"], "danger")
        return render_template('professors/create.html', form={"name": name, "email": email}), HTTP_BAD_REQUEST

    flash("Profesor creado exitosamente.", "success")
    return redirect('/professors')

@professor_bp.route('/professors/<int:id>/edit')
def edit_professor_form(id):
    professor = service.get_professor_by_id(id)
    if not professor:
        flash("Profesor no encontrado.", "danger")
        return redirect('/professors')
    return render_template('professors/edit.html', form=professor)

@professor_bp.route('/professors/<int:id>/edit', methods=['POST'])
def edit_professor(id):
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if not name or not email:
        flash("Todos los campos son obligatorios.", "danger")
        return render_template('professors/edit.html', form={"id": id, "name": name, "email": email}), HTTP_BAD_REQUEST

    result = service.update_professor(id, name, email)
    if not result["success"]:
        flash(result["message"], "danger")
        return render_template('professors/edit.html', form={"id": id, "name": name, "email": email}), HTTP_BAD_REQUEST

    flash("Profesor actualizado correctamente.", "success")
    return redirect(f'/professors/{id}')

@professor_bp.route('/professors/<int:id>/delete', methods=['POST'])
def delete_professor(id):
    result = service.delete_professor(id)
    if not result["success"]:
        flash(result["message"], "danger")
    else:
        flash("Profesor eliminado exitosamente.", "success")
    return redirect('/professors')

@professor_bp.route('/professors/delete-all', methods=['POST'])
def delete_all_professors():
    result = service.delete_all_professors()
    if not result["success"]:
        flash(result["message"], "danger")
    else:
        flash("Todos los profesores han sido eliminados exitosamente.", "success")
    return redirect('/professors')