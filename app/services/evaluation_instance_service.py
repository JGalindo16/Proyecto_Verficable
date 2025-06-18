from app.db import DatabaseConnection
from app.http_errors import HTTP_BAD_REQUEST, HTTP_OK
from app.sql_queries import evaluation_instance_queries as q

class EvaluationInstanceService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def get_instances_by_evaluation(self, evaluation_id: int):
        self.cursor.execute(q.GET_INSTANCES_BY_EVALUATION, (evaluation_id,))
        return self.cursor.fetchall()

    def get_total_specific_weight_by_evaluation(self, evaluation_id: int, exclude_instance_id=None):
        if exclude_instance_id:
            self.cursor.execute(q.GET_TOTAL_WEIGHT_EXCLUDE, (evaluation_id, exclude_instance_id))
        else:
            self.cursor.execute(q.GET_TOTAL_WEIGHT, (evaluation_id,))
        row = self.cursor.fetchone()
        return row["total"] if row else 0

    def add_instance(self, evaluation_id: int, name: str, specific_weight: float, mandatory: bool):
        try:
            self.cursor.execute(q.CHECK_DUPLICATE_NAME_ON_CREATE, (evaluation_id, name))
            if self.cursor.fetchone()["already_exists"]:
                return {"success": False, "message": "Ya existe una instancia con ese nombre para esta evaluación"}

            self.cursor.execute(q.INSERT_EVALUATION_INSTANCE, (evaluation_id, name, specific_weight, mandatory))
            instance_eval_id = self.cursor.lastrowid

            self.cursor.execute(q.GET_SECTION_ID_BY_EVALUATION, (evaluation_id,))
            result = self.cursor.fetchone()
            if not result:
                return {"success": False, "message": "Evaluación sin sección asociada"}

            section_id = result["section_id"]
            self.cursor.execute(q.GET_ENROLLMENTS_BY_SECTION, (section_id,))
            enrollments = self.cursor.fetchall()

            if enrollments:
                self.cursor.executemany(q.BULK_INSERT_GRADES, [
                    (instance_eval_id, row["enrollment_id"], 1.0) for row in enrollments
                ])

            self.db.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": "Error inesperado al agregar la instancia"}

    def update_instance(self, evaluation_id: int, instance_eval_id: int, name: str, specific_weight: float, mandatory: bool):
        try:
            self.cursor.execute(q.CHECK_DUPLICATE_NAME_ON_UPDATE, (evaluation_id, name, instance_eval_id))
            if self.cursor.fetchone():
                return {"success": False, "message": "Ya existe otra instancia con ese nombre para esta evaluación"}

            self.cursor.execute(q.UPDATE_INSTANCE, (name, specific_weight, mandatory, instance_eval_id))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": "Error al actualizar la instancia"}

    def delete_instance(self, instance_eval_id: int):
        try:
            self.cursor.execute(q.DELETE_INSTANCE, (instance_eval_id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            return HTTP_BAD_REQUEST
