from app.db import DatabaseConnection
from app.http_errors import HTTP_BAD_REQUEST, HTTP_OK
from app.sql_queries import course_queries as q
import json

class CourseService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_course(self, name: str, code: str):
        if not name or not code:
            return {"success": False, "message": "Todos los campos son obligatorios"}

        self.cursor.execute(q.CHECK_COURSE_NAME_CODE_EXISTS, (name, code))
        result = self.cursor.fetchone()
        if result["name_exists"]:
            return {"success": False, "message": "Ya existe un curso con ese nombre"}
        if result["code_exists"]:
            return {"success": False, "message": "Ya existe un curso con ese código"}

        try:
            self.cursor.execute(q.INSERT_COURSE, (name, code))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al insertar curso:", e)
            return {"success": False, "message": "Error al insertar en la base de datos"}

    def get_all_courses(self):
        self.cursor.execute(q.GET_ALL_COURSES)
        return self.cursor.fetchall()

    def get_course_by_id(self, id: int):
        self.cursor.execute(q.GET_COURSE_BY_ID, (id,))
        course = self.cursor.fetchone()

        if course:
            from app.services.course_instance_service import CourseInstanceService
            instance_service = CourseInstanceService()
            course["instances"] = instance_service.get_instances_by_course(id)

        return course

    def update_course(self, id: int, name: str, code: str):
        if not name or not code:
            return {"success": False, "message": "Todos los campos son obligatorios"}

        self.cursor.execute(q.CHECK_DUPLICATE_COURSE_ON_UPDATE, (name, id, code, id))
        result = self.cursor.fetchone()
        if result["name_exists"]:
            return {"success": False, "message": "Ya existe otro curso con ese nombre"}
        if result["code_exists"]:
            return {"success": False, "message": "Ya existe otro curso con ese código"}

        try:
            self.cursor.execute(q.UPDATE_COURSE, (name, code, id))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al actualizar curso:", e)
            return {"success": False, "message": "Error al actualizar el curso"}

    def delete_course(self, id: int):
        try:
            self.cursor.execute(q.DELETE_COURSE, (id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar curso:", e)
            return HTTP_BAD_REQUEST

    def process_json(self, file_obj):
        try:
            courses = json.load(file_obj)
            values = [(c['name'], c['code']) for c in courses]
            self.cursor.executemany(q.INSERT_COURSE, values)
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al procesar JSON:", e)
            return {"success": False, "message": "Error al procesar el archivo JSON"}