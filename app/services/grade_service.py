from app.db import DatabaseConnection
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

    def _get_enrollment_id(self, section_id: int, student_id: int):
        self.cursor.execute(GET_ENROLLMENT_ID, (section_id, student_id))
        result = self.cursor.fetchone()
        return result["enrollment_id"] if result else None

    def _get_existing_grade(self, instance_eval_id: int, enrollment_id: int):
        self.cursor.execute(GET_EXISTING_GRADE, (instance_eval_id, enrollment_id))
        return self.cursor.fetchone()

    def _save_grade(self, instance_eval_id: int, enrollment_id: int, 
                   score: float, is_update: bool = False):
        if is_update:
            self.cursor.execute(
                UPDATE_GRADE, (score, instance_eval_id, enrollment_id)
            )
        else:
            self.cursor.execute(
                INSERT_GRADE, (instance_eval_id, enrollment_id, score)
            )
        self.db.commit()

    def _calculate_averages(self, enrollment_id: int):
        self.cursor.execute(GET_ALL_GRADES_FOR_ENROLLMENT, (enrollment_id,))
        rows = self.cursor.fetchall()

        if not rows:
            return 0.0, 0.0, None

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
        current_eval_type = rows[0]['eval_type'] if rows else None

        return (
            type_avgs.get(current_eval_type, 1.0),
            final_avg,
            current_eval_type
        )

    def create_or_update_grade(self, section_id: int, student_id: int,
                              instance_eval_id: int, score: float):
        try:
            enrollment_id = self._get_enrollment_id(section_id, student_id)
            if not enrollment_id:
                return {
                    "success": False,
                    "message": "Inscripción no encontrada",
                    "type_average": None,
                    "final_average": None
                }

            existing = self._get_existing_grade(instance_eval_id, enrollment_id)

            self._save_grade(
                instance_eval_id, enrollment_id, score, bool(existing)
            )

            type_avg, final_avg, eval_type = self._calculate_averages(
                enrollment_id
            )

            return {
                "success": True,
                "message": "Nota actualizada correctamente",
                "type_average": round(type_avg, 1),
                "final_average": round(final_avg, 1)
            }

        except Exception:
            return {
                "success": False,
                "type_average": None,
                "final_average": None
            }