from app.db import DatabaseConnection
from app.http_errors import HTTP_BAD_REQUEST, HTTP_OK
from app.sql_queries import evaluation_queries as q

class EvaluationService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_evaluation(self, section_id: int, type_: str, weight: float, optional: bool):
        try:
            self.cursor.execute(q.CHECK_DUPLICATE_TYPE_ON_CREATE, (section_id, type_))
            if self.cursor.fetchone()["already_exists"]:
                return {"success": False, "message": "Ya existe una evaluación con ese nombre en esta sección."}

            self.cursor.execute(q.INSERT_EVALUATION, (section_id, type_, weight, optional))
            evaluation_id = self.cursor.lastrowid

            self.cursor.execute(q.INSERT_DEFAULT_INSTANCE, (evaluation_id, f"{type_} 1", 1.0, True))
            instance_eval_id = self.cursor.lastrowid

            self.cursor.execute(q.GET_ENROLLMENTS_BY_SECTION, (section_id,))
            enrollments = self.cursor.fetchall()

            if enrollments:
                self.cursor.executemany(q.BULK_INSERT_INITIAL_GRADES, [
                    (instance_eval_id, row["enrollment_id"], 1.0) for row in enrollments
                ])

            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al insertar evaluación con notas 0:", e)
            return {"success": False, "message": "Error interno al crear evaluación."}

    def get_all_evaluations_by_section(self, section_id: int):
        self.cursor.execute(q.GET_ALL_BY_SECTION, (section_id,))
        return self.cursor.fetchall()

    def get_evaluation_by_id(self, evaluation_id: int):
        self.cursor.execute(q.GET_BY_ID, (evaluation_id,))
        return self.cursor.fetchone()

    def update_evaluation(self, evaluation_id: int, type_: str, weight: float, optional: bool):
        try:
            self.cursor.execute(q.CHECK_DUPLICATE_TYPE_ON_UPDATE, (type_, evaluation_id))
            if self.cursor.fetchone()["already_exists"]:
                return {"success": False, "message": "Ya existe otra evaluación con ese nombre."}

            self.cursor.execute(q.UPDATE_EVALUATION, (type_, weight, optional, evaluation_id))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al actualizar evaluación:", e)
            return {"success": False, "message": "Error interno al actualizar evaluación."}

    def delete_evaluation(self, evaluation_id: int):
        try:
            self.cursor.execute(q.DELETE_EVALUATION, (evaluation_id,))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al eliminar evaluación:", e)
            return {"success": False, "message": "Error interno al eliminar evaluación."}

    def get_total_weight_by_section(self, section_id: int):
        self.cursor.execute(q.GET_TOTAL_WEIGHT_BY_SECTION, (section_id,))
        result = self.cursor.fetchone()
        return result["total"] if result else 0