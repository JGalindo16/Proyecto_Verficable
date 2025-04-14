from app.db import DatabaseConnection
from app.http_errors import HTTP_BAD_REQUEST, HTTP_OK
import json

class CourseService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_course(self, name: str, code: str):
        try:
            sql = "INSERT INTO courses (name, code) VALUES (%s, %s)"
            self.cursor.execute(sql, (name, code))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al insertar curso:", e)
            return HTTP_BAD_REQUEST

    def get_all_courses(self):
        self.cursor.execute("SELECT * FROM courses")
        return self.cursor.fetchall()

    def get_course_by_id(self, id: int):
        self.cursor.execute("SELECT * FROM courses WHERE id = %s", (id,))
        return self.cursor.fetchone()

    def update_course(self, id: int, name: str, code: str):
        try:
            sql = "UPDATE courses SET name = %s, code = %s WHERE id = %s"
            self.cursor.execute(sql, (name, code, id))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al actualizar curso:", e)
            return HTTP_BAD_REQUEST

    def delete_course(self, id: int):
        try:
            sql = "DELETE FROM courses WHERE id = %s"
            self.cursor.execute(sql, (id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar curso:", e)
            return HTTP_BAD_REQUEST

    def process_json(self, file_obj):
        try:
            courses = json.load(file_obj)
            values = [(c['name'], c['code']) for c in courses]
            sql = "INSERT INTO courses (name, code) VALUES (%s, %s)"
            self.cursor.executemany(sql, values)
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al procesar JSON:", e)
            return HTTP_BAD_REQUEST