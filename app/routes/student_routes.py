from flask import Blueprint, render_template, request, redirect, flash
from app.services.student_service import StudentService
from app.http_errors import HTTP_BAD_REQUEST
from app.alertas.students_alerts import *

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
        flash(ESTUDIANTES_NO_ENCONTRADO, "danger")
        return redirect('/students')
    return render_template('students/show.html', data=student)

@student_bp.route('/students/create')
def create_student_form():
    return render_template('students/create.html', form={"name": "", "email": "", "admission_date": ""})

@student_bp.route('/students', methods=['POST'])
def create_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    admission_date = request.form.get("admission_date", "").strip()

    if not name or not email or not admission_date:
        flash(TODOS_LOS_CAMPOS_OBLIGATORIOS, "danger")
        return render_template('students/create.html', form={"name": name, "email": email, "admission_date": admission_date}), HTTP_BAD_REQUEST

    result = service.add_student(name, email, admission_date)
    if not result["success"]:
        flash(result["message"], "danger")
        return render_template('students/create.html', form={"name": name, "email": email, "admission_date": admission_date}), HTTP_BAD_REQUEST

    flash(ESTUDIANTE_CREADO_EXITOSAMENTE, "success")
    return redirect('/students')

@student_bp.route('/students/<int:id>/edit')
def edit_student_form(id):
    student = service.get_student_by_id(id)
    if not student:
        flash(ESTUDIANTES_NO_ENCONTRADO, "danger")
        return redirect('/students')
    return render_template('students/edit.html', form=student)

@student_bp.route('/students/<int:id>/edit', methods=['POST'])
def edit_student(id):
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    admission_date = request.form.get("admission_date", "").strip()

    if not name or not email or not admission_date:
        flash(TODOS_LOS_CAMPOS_OBLIGATORIOS, "danger")
        return render_template('students/edit.html', form={"id": id, "name": name, "email": email, "admission_date": admission_date}), HTTP_BAD_REQUEST

    result = service.update_student(id, name, email, admission_date)
    if not result["success"]:
        flash(result["message"], "danger")
        return render_template('students/edit.html', form={"id": id, "name": name, "email": email, "admission_date": admission_date}), HTTP_BAD_REQUEST

    flash(ESTUDIANTE_CREADO_EXITOSAMENTE, "success")
    return redirect(f'/students/{id}')

@student_bp.route('/students/<int:id>/delete', methods=['POST'])
def delete_student(id):
    result = service.delete_student(id)
    if not result["success"]:
        flash(result["message"], "danger")
    else:
        flash(ESTUDIANTE_ELIMINADO_EXITOSAMENTE, "success")
    return redirect('/students')

@student_bp.route('/students/delete-all', methods=['POST'])
def delete_all_students():
    result = service.delete_all_students()
    if not result["success"]:
        flash(result["message"], "danger")
    else:
        flash(TODOS_LOS_ESTUDIANTES_ELIMINADOS, "success")
    return redirect('/students')