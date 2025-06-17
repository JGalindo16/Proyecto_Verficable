from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
from app.sql_queries import course_instance_queries as q


class CourseInstanceService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_instance(self, course_id: int, year: int, semester: str):
        if not year or not semester:
            return {"success": False, "message": "Todos los campos son obligatorios"}

        self.cursor.execute(q.CHECK_INSTANCE_EXISTS, (course_id, year, semester))
        if self.cursor.fetchone()['count'] > 0:
            return {"success": False, "message": "Ya existe una instancia con el mismo año y semestre para este curso"}

        try:
            self.cursor.execute(q.INSERT_INSTANCE, (course_id, year, semester))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al insertar instancia:", e)
            return {"success": False, "message": str(e)}

    def get_instances_by_course(self, course_id: int):
        self.cursor.execute(q.GET_INSTANCES_BY_COURSE, (course_id,))
        return self.cursor.fetchall()

    def delete_instance(self, instance_id: int):
        try:
            self.cursor.execute(q.DELETE_INSTANCE, (instance_id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar instancia:", e)
            return HTTP_BAD_REQUEST

    def update_instance(self, instance_id: int, year: int, semester: str):
        if not year or not semester:
            return {"success": False, "message": "Todos los campos son obligatorios"}

        self.cursor.execute(q.GET_INSTANCE_BY_ID, (instance_id,))
        current = self.cursor.fetchone()
        if not current:
            return {"success": False, "message": "Instancia no encontrada"}

        course_id = current['course_id']

        self.cursor.execute(q.CHECK_DUPLICATE_INSTANCE_ON_UPDATE, (course_id, year, semester, instance_id))
        if self.cursor.fetchone()['count'] > 0:
            return {"success": False, "message": "Ya existe otra instancia con el mismo año y semestre para este curso"}

        try:
            self.cursor.execute(q.UPDATE_INSTANCE, (year, semester, instance_id))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al actualizar instancia:", e)
            return {"success": False, "message": str(e)}

    def get_instance_by_id(self, instance_id: int):
        self.cursor.execute(q.GET_INSTANCE_BY_ID, (instance_id,))
        return self.cursor.fetchone()

    def get_enrolled_student_ids(self, section_id: int):
        self.cursor.execute(q.GET_ENROLLED_STUDENT_IDS, (section_id,))
        result = self.cursor.fetchall()
        return [row['student_id'] for row in result]

    def add_evaluation_instance(self, evaluation_id, name, specific_weight, mandatory=True):
        self.cursor.execute(q.GET_TOTAL_WEIGHT_BY_EVALUATION, (evaluation_id,))
        result = self.cursor.fetchone()
        current_weight = result['total_weight'] if result['total_weight'] else 0

        if current_weight + specific_weight > 1.001:
            return {"success": False, "message": "La suma de los pesos excede el 100%."}

        try:
            self.cursor.execute(
                q.INSERT_EVALUATION_INSTANCE,
                (evaluation_id, name, specific_weight, mandatory)
            )
            self.db.commit()
            return {"success": True, "id": self.cursor.lastrowid}
        except Exception as e:
            print("Error al insertar instancia de evaluación:", e)
            return {"success": False, "message": str(e)}

    def update_evaluation_instance(self, instance_eval_id, name, specific_weight, mandatory=None):
        try:
            self.cursor.execute(q.GET_EVALUATION_INSTANCE_DATA, (instance_eval_id,))
            current = self.cursor.fetchone()
            if not current:
                return {"success": False, "message": "Instancia de evaluación no encontrada."}

            evaluation_id = current['evaluation_id']
            old_weight = current['specific_weight']

            self.cursor.execute(q.GET_OTHER_TOTAL_WEIGHT, (evaluation_id, instance_eval_id))
            result = self.cursor.fetchone()
            other_weights = result['total_weight'] if result and result['total_weight'] else 0

            if other_weights + specific_weight > 1.001:
                return {
                    "success": False,
                    "message": f"La suma de los pesos específicos excedería el 100%. Otros: {other_weights * 100}%, Nuevo: {specific_weight * 100}%"
                }

            if mandatory is not None:
                self.cursor.execute(
                    q.UPDATE_EVALUATION_INSTANCE_WITH_MANDATORY + " " + q.UPDATE_EVALUATION_INSTANCE_WHERE,
                    (name, specific_weight, mandatory, instance_eval_id)
                )
            else:
                self.cursor.execute(
                    q.UPDATE_EVALUATION_INSTANCE_BASE + " " + q.UPDATE_EVALUATION_INSTANCE_WHERE,
                    (name, specific_weight, instance_eval_id)
                )

            self.db.commit()
            return {"success": True}

        except Exception as e:
            print("Error al actualizar instancia de evaluación:", e)
            return {"success": False, "message": str(e)}

    def redistribute_weights_after_delete(self, evaluation_id):
        try:
            self.cursor.execute(q.COUNT_INSTANCES_BY_EVALUATION, (evaluation_id,))
            count = self.cursor.fetchone()['count']
            if count == 0:
                return {"success": True, "message": "No hay instancias que actualizar."}

            new_weight = 1.0 / count
            self.cursor.execute(q.REDISTRIBUTE_EVALUATION_WEIGHTS, (new_weight, evaluation_id))
            self.db.commit()
            return {"success": True}
        except Exception as e:
            print("Error al redistribuir pesos:", e)
            return {"success": False, "message": str(e)}