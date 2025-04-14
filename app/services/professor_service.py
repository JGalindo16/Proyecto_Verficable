from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST

class ProfessorService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_professor(self, name: str, email: str):
        try:
            sql = "INSERT INTO professors (name, email) VALUES (%s, %s)"
            self.cursor.execute(sql, (name, email))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al insertar profesor:", e)
            return HTTP_BAD_REQUEST

    def get_all_professors(self):
        # Alias para usar `id` en templates sin tener que cambiar HTML
        self.cursor.execute("SELECT professor_id AS id, name, email FROM professors")
        return self.cursor.fetchall()

    def get_professor_by_id(self, id: int):
        self.cursor.execute("SELECT professor_id AS id, name, email FROM professors WHERE professor_id = %s", (id,))
        return self.cursor.fetchone()

    def update_professor(self, id: int, name: str, email: str):
        try:
            sql = "UPDATE professors SET name = %s, email = %s WHERE professor_id = %s"
            self.cursor.execute(sql, (name, email, id))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al actualizar profesor:", e)
            return HTTP_BAD_REQUEST

    def delete_professor(self, id: int):
        try:
            sql = "DELETE FROM professors WHERE professor_id = %s"
            self.cursor.execute(sql, (id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar profesor:", e)
            return HTTP_BAD_REQUEST