from app.db import DatabaseConnection
from app.http_errors import HTTP_BAD_REQUEST, HTTP_OK

class EvaluationService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_evaluation(self, section_id: int, type_: str, weight: float, optional: bool):
        try:
            # 1. Insertar evaluación
            sql_eval = "INSERT INTO evaluations (section_id, type, weight, optional) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(sql_eval, (section_id, type_, weight, optional))
            evaluation_id = self.cursor.lastrowid

            # 2. Crear instancia por defecto para esa evaluación
            sql_instance = """
                INSERT INTO evaluation_instances (evaluation_id, name, specific_weight, mandatory)
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql_instance, (evaluation_id, f"{type_} 1", 1.0, True))
            instance_eval_id = self.cursor.lastrowid

            # 3. Obtener estudiantes inscritos
            self.cursor.execute("SELECT enrollment_id FROM enrollments WHERE section_id = %s", (section_id,))
            enrollments = self.cursor.fetchall()

            # 4. Si hay estudiantes, crear notas en 0
            if enrollments:
                
                sql_grade = """
                    INSERT INTO grades (instance_eval_id, enrollment_id, score)
                    VALUES (%s, %s, %s)
                """
                grade_values = [(instance_eval_id, row["enrollment_id"], 0.0) for row in enrollments]
                self.cursor.executemany(sql_grade, grade_values)

            self.db.commit()
            return HTTP_OK

        except Exception as e:
            print("Error al insertar evaluación con notas 0:", e)
            return HTTP_BAD_REQUEST

    def get_all_evaluations_by_section(self, section_id: int):
        self.cursor.execute("""
            SELECT evaluation_id AS id, type, weight, optional
            FROM evaluations
            WHERE section_id = %s
        """, (section_id,))
        return self.cursor.fetchall()

    def get_evaluation_by_id(self, evaluation_id: int):
        self.cursor.execute("""
            SELECT evaluation_id AS id, type, weight, optional, section_id
            FROM evaluations
            WHERE evaluation_id = %s
        """, (evaluation_id,))
        return self.cursor.fetchone()

    def update_evaluation(self, evaluation_id: int, type_: str, weight: float, optional: bool):
        try:
            sql = "UPDATE evaluations SET type = %s, weight = %s, optional = %s WHERE evaluation_id = %s"
            self.cursor.execute(sql, (type_, weight, optional, evaluation_id))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al actualizar evaluación:", e)
            return HTTP_BAD_REQUEST

    def delete_evaluation(self, evaluation_id: int):
        try:
            sql = "DELETE FROM evaluations WHERE evaluation_id = %s"
            self.cursor.execute(sql, (evaluation_id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar evaluación:", e)
            return HTTP_BAD_REQUEST
    
    def get_total_weight_by_section(self, section_id: int):
        self.cursor.execute("""
            SELECT COALESCE(SUM(weight), 0) AS total
            FROM evaluations
            WHERE section_id = %s
        """, (section_id,))
        result = self.cursor.fetchone()
        return result["total"] if result else 0