from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
import app.sql_queries.professor_queries as q

class ProfessorService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_professor(self, name: str, email: str):
        try:
            self.cursor.execute(q.INSERT_PROFESSOR, (name, email))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": "Error al registrar el profesor."}

    def get_all_professors(self):
        self.cursor.execute(q.GET_ALL_PROFESSORS)
        return self.cursor.fetchall()

    def get_professor_by_id(self, id: int):
        self.cursor.execute(q.GET_PROFESSOR_BY_ID, (id,))
        return self.cursor.fetchone()

    def update_professor(self, id: int, name: str, email: str):
        try:
            self.cursor.execute(q.UPDATE_PROFESSOR, (name, email, id))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": "Error al actualizar los datos del profesor."}

    def delete_professor(self, id: int):
        try:
            self.cursor.execute(q.DELETE_PROFESSOR, (id,))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": "Error al eliminar el profesor."}

    def delete_all_professors(self):
        try:
            self.cursor.execute(q.DELETE_ALL_PROFESSORS)
            self.cursor.execute("ALTER TABLE professors AUTO_INCREMENT = 1")
            self.cursor.execute("ALTER TABLE sections AUTO_INCREMENT = 1")
            self.cursor.execute("ALTER TABLE evaluations AUTO_INCREMENT = 1")
            self.cursor.execute("ALTER TABLE evaluation_instances AUTO_INCREMENT = 1")
            self.cursor.execute("ALTER TABLE enrollments AUTO_INCREMENT = 1")
            self.db.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": "Error al eliminar todos los profesores."}