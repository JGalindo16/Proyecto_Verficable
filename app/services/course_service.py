from app.db import DatabaseConnection
from app.http_errors import HTTP_BAD_REQUEST, HTTP_OK
import json

class CourseService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_course(self, name: str, code: str):
        try:
            sql = f"INSERT INTO courses (name, code) VALUES ('{name}', '{code}')"
            self.cursor.execute(sql)
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error:", e)
            return HTTP_BAD_REQUEST

    def get_all_courses(self):
        self.cursor.execute("SELECT * FROM courses")
        return self.cursor.fetchall()

    def get_course_by_id(self, id: int):
        self.cursor.execute(f"SELECT * FROM courses WHERE id = {id}")
        return self.cursor.fetchone()

    def process_json(self, file_obj):
        try:
            courses = json.load(file_obj)
            values = ", ".join([f"('{c['name']}', '{c['code']}')" for c in courses])
            sql = f"INSERT INTO courses (name, code) VALUES {values}"
            self.cursor.execute(sql)
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error:", e)
            return HTTP_BAD_REQUEST