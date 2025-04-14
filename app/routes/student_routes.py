from flask import Blueprint, render_template, request, redirect
from app.services.student_service import StudentService
from app.http_errors import HTTP_BAD_REQUEST

student_bp = Blueprint('student', __name__)
service = StudentService()

@student_bp.route('/students')
def get_all_students():
    students = service.get_all_students()
    return render_template('students/index.html', data=students)

@student_bp.route('/students/<int:id>')
def get_student(id):
    student = service.get_student_by_id(id)
    if not student:
        return "Estudiante no encontrado", 404
    return render_template('students/show.html', data=student)

@student_bp.route('/students/create')
def create_student_form():
    return render_template('students/create.html', form={"name": "", "email": "", "admission_date": ""})

@student_bp.route('/students', methods=['POST'])
def create_student():
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    admission_date = request.form.get("admission_date", "")
    if not name or not email or not admission_date:
        return render_template('students/create.html', error="Todos los campos son obligatorios", form={"name": name, "email": email, "admission_date": admission_date}), HTTP_BAD_REQUEST
    service.add_student(name, email, admission_date)
    return redirect('/students')

@student_bp.route('/students/<int:id>/edit')
def edit_student_form(id):
    student = service.get_student_by_id(id)
    if not student:
        return "Estudiante no encontrado", 404
    return render_template('students/edit.html', form=student)

@student_bp.route('/students/<int:id>/edit', methods=['POST'])
def edit_student(id):
    name = request.form.get("name")
    email = request.form.get("email")
    admission_date = request.form.get("admission_date")
    if not name or not email or not admission_date:
        return render_template('students/edit.html', form={"id": id, "name": name, "email": email, "admission_date": admission_date}, error="Todos los campos son obligatorios"), HTTP_BAD_REQUEST
    service.update_student(id, name, email, admission_date)
    return redirect(f'/students/{id}')

@student_bp.route('/students/<int:id>/delete', methods=['POST'])
def delete_student(id):
    service.delete_student(id)
    return redirect('/students')