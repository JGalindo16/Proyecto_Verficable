from app.db import DatabaseConnection
from app.http_errors import HTTP_BAD_REQUEST, HTTP_OK

class EvaluationInstanceService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def get_instances_by_evaluation(self, evaluation_id: int):
        self.cursor.execute("""
            SELECT instance_eval_id AS id, name, specific_weight, mandatory
            FROM evaluation_instances
            WHERE evaluation_id = %s
        """, (evaluation_id,))
        return self.cursor.fetchall()

    def get_total_specific_weight_by_evaluation(self, evaluation_id: int, exclude_instance_id=None):
        if exclude_instance_id:
            self.cursor.execute("""
                SELECT COALESCE(SUM(specific_weight), 0) AS total
                FROM evaluation_instances
                WHERE evaluation_id = %s AND instance_eval_id != %s
            """, (evaluation_id, exclude_instance_id))
        else:
            self.cursor.execute("""
                SELECT COALESCE(SUM(specific_weight), 0) AS total
                FROM evaluation_instances
                WHERE evaluation_id = %s
            """, (evaluation_id,))
        row = self.cursor.fetchone()
        return row["total"] if row else 0

    def add_instance(self, evaluation_id: int, name: str, specific_weight: float, mandatory: bool):
        try:
            self.cursor.execute("""
                INSERT INTO evaluation_instances (evaluation_id, name, specific_weight, mandatory)
                VALUES (%s, %s, %s, %s)
            """, (evaluation_id, name, specific_weight, mandatory))
            instance_eval_id = self.cursor.lastrowid

            self.cursor.execute("""
                SELECT section_id FROM evaluations WHERE evaluation_id = %s
            """, (evaluation_id,))
            result = self.cursor.fetchone()
            if not result:
                return HTTP_BAD_REQUEST
            section_id = result["section_id"]

            self.cursor.execute("SELECT enrollment_id FROM enrollments WHERE section_id = %s", (section_id,))
            enrollments = self.cursor.fetchall()

            if enrollments:
                self.cursor.executemany("""
                    INSERT INTO grades (instance_eval_id, enrollment_id, score)
                    VALUES (%s, %s, %s)
                """, [(instance_eval_id, row["enrollment_id"], 0.0) for row in enrollments])

            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al agregar instancia:", e)
            return HTTP_BAD_REQUEST

    def update_instance(self, instance_eval_id: int, name: str, specific_weight: float, mandatory: bool):
        try:
            self.cursor.execute("""
                UPDATE evaluation_instances
                SET name = %s, specific_weight = %s, mandatory = %s
                WHERE instance_eval_id = %s
            """, (name, specific_weight, mandatory, instance_eval_id))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al actualizar instancia:", e)
            return HTTP_BAD_REQUEST

    def delete_instance(self, instance_eval_id: int):
        try:
            self.cursor.execute("DELETE FROM evaluation_instances WHERE instance_eval_id = %s", (instance_eval_id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar instancia:", e)
            return HTTP_BAD_REQUEST