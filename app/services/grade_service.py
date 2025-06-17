from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
from app.sql_queries.grade_queries import (
    GET_SECTION_GRADES,
    GET_COURSE_INFO,
    GET_ENROLLMENT_ID,
    GET_EXISTING_GRADE,
    INSERT_GRADE,
    UPDATE_GRADE,
    GET_ALL_GRADES_FOR_ENROLLMENT
)

class GradeService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def get_section_grades(self, section_id):
        self.cursor.execute(GET_SECTION_GRADES, (section_id,))
        return self.cursor.fetchall()

    def get_course_info_for_grades(self, course_id, instance_id):
        self.cursor.execute(GET_COURSE_INFO, (course_id, instance_id))
        return self.cursor.fetchone()

    def create_or_update_grade(self, section_id: int, student_id: int, instance_eval_id: int, score: float):
        try:
            self.cursor.execute(GET_ENROLLMENT_ID, (section_id, student_id))
            result = self.cursor.fetchone()
            if not result:
                return False, "Inscripción no encontrada", None, None

            enrollment_id = result["enrollment_id"]

            self.cursor.execute(GET_EXISTING_GRADE, (instance_eval_id, enrollment_id))
            existing = self.cursor.fetchone()

            if existing:
                self.cursor.execute(UPDATE_GRADE, (score, instance_eval_id, enrollment_id))
            else:
                self.cursor.execute(INSERT_GRADE, (instance_eval_id, enrollment_id, score))

            self.db.commit()

            self.cursor.execute(GET_ALL_GRADES_FOR_ENROLLMENT, (enrollment_id,))
            rows = self.cursor.fetchall()

            if not rows:
                return True, "Nota actualizada correctamente", 0.0, 0.0

            type_totals = {}
            type_weights = {}
            eval_weights = {}

            for row in rows:
                etype = row['eval_type']
                ew = row['eval_weight']
                sw = row['specific_weight']
                s = row['score']

                if etype not in type_totals:
                    type_totals[etype] = 0.0
                    type_weights[etype] = 0.0
                    eval_weights[etype] = ew

                type_totals[etype] += s * sw
                type_weights[etype] += sw

            type_avgs = {
                k: (type_totals[k] / type_weights[k]) if type_weights[k] else 0.0
                for k in type_totals
            }

            final_avg = sum(type_avgs[t] * eval_weights[t] for t in type_avgs)
            eval_type = row['eval_type'] if rows else None

            return {
                "success": True,
                "type_average": round(type_avgs.get(row['eval_type'], 1.0), 1),
                "final_average": round(final_avg, 1)
            }

        except Exception as e:
            return {
                "success": False,
                "type_average": None,
                "final_average": None
            }