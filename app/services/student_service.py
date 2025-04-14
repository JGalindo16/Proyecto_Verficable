from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST

class StudentService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_student(self, name: str, email: str, admission_date: str):
        try:
            sql = "INSERT INTO students (name, email, admission_date) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (name, email, admission_date))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al insertar estudiante:", e)
            return HTTP_BAD_REQUEST

    def get_all_students(self):
        self.cursor.execute("SELECT student_id AS id, name, email, admission_date FROM students")
        return self.cursor.fetchall()

    def get_student_by_id(self, id: int):
        self.cursor.execute("SELECT student_id AS id, name, email, admission_date FROM students WHERE student_id = %s", (id,))
        return self.cursor.fetchone()

    def update_student(self, id: int, name: str, email: str, admission_date: str):
        try:
            sql = "UPDATE students SET name = %s, email = %s, admission_date = %s WHERE student_id = %s"
            self.cursor.execute(sql, (name, email, admission_date, id))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al actualizar estudiante:", e)
            return HTTP_BAD_REQUEST

    def delete_student(self, id: int):
        try:
            sql = "DELETE FROM students WHERE student_id = %s"
            self.cursor.execute(sql, (id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar estudiante:", e)
            return HTTP_BAD_REQUEST