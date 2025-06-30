from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
from app.sql_queries.student_queries import (
    INSERT_STUDENT,
    SELECT_ALL_STUDENTS,
    SELECT_STUDENT_BY_ID,
    UPDATE_STUDENT,
    DELETE_STUDENT,
    DELETE_ALL_STUDENTS
)

from app.alertas.students_alerts import (
    ESTUDIANTE_CREADO_EXITOSAMENTE,
    ESTUDIANTE_ACTUALIZADO_EXITOSAMENTE,
    ESTUDIANTE_ELIMINADO_EXITOSAMENTE,
    TODOS_LOS_ESTUDIANTES_ELIMINADOS,
    ERROR_AL_CREAR_ESTUDIANTE,
    ERROR_AL_ACTUALIZAR_ESTUDIANTE,
    ERROR_AL_ELIMINAR_ESTUDIANTE,
    ERROR_AL_ELIMINAR_TODOS
)

class StudentService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_student(self, name: str, email: str, admission_date: str):
        try:
            self.cursor.execute(INSERT_STUDENT, (name, email, admission_date))
            self.db.commit()
            return {"success": True, "message": ESTUDIANTE_CREADO_EXITOSAMENTE, "status_code": HTTP_OK}
        except Exception as e:
            return {"success": False, "message": f"{ERROR_AL_CREAR_ESTUDIANTE}: {str(e)}", "status_code": HTTP_BAD_REQUEST}

    def get_all_students(self):
        self.cursor.execute(SELECT_ALL_STUDENTS)
        return self.cursor.fetchall()

    def get_student_by_id(self, id: int):
        self.cursor.execute(SELECT_STUDENT_BY_ID, (id,))
        return self.cursor.fetchone()

    def update_student(self, id: int, name: str, email: str, admission_date: str):
        try:
            self.cursor.execute(UPDATE_STUDENT, (name, email, admission_date, id))
            self.db.commit()
            return {"success": True, "message": ESTUDIANTE_ACTUALIZADO_EXITOSAMENTE, "status_code": HTTP_OK}
        except Exception as e:
            return {"success": False, "message": f"{ERROR_AL_ACTUALIZAR_ESTUDIANTE}: {str(e)}", "status_code": HTTP_BAD_REQUEST}

    def delete_student(self, id: int):
        try:
            self.cursor.execute(DELETE_STUDENT, (id,))
            self.db.commit()
            return {"success": True, "message": ESTUDIANTE_ELIMINADO_EXITOSAMENTE, "status_code": HTTP_OK}
        except Exception as e:
            return {"success": False, "message": f"{ERROR_AL_ELIMINAR_ESTUDIANTE}: {str(e)}", "status_code": HTTP_BAD_REQUEST}

    def delete_all_students(self):
        try:
            self.cursor.execute(DELETE_ALL_STUDENTS)
            self.cursor.execute("ALTER TABLE students AUTO_INCREMENT = 1")
            self.cursor.execute("ALTER TABLE enrollments AUTO_INCREMENT = 1")
            self.cursor.execute("ALTER TABLE grades AUTO_INCREMENT = 1")
            self.db.commit()
            return {"success": True, "message": TODOS_LOS_ESTUDIANTES_ELIMINADOS, "status_code": HTTP_OK}
        except Exception as e:
            return {"success": False, "message": f"{ERROR_AL_ELIMINAR_TODOS}: {str(e)}", "status_code": HTTP_BAD_REQUEST}