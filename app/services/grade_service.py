from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST

class GradeService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def get_course_grades(self, course_id, instance_id):
        """Obtener todas las notas para un curso específico en una instancia"""
        self.cursor.execute("""
            SELECT 
                s.section_id,
                s.number as section_number,
                st.student_id,
                st.name as student_name,
                e.type as evaluation_type,
                e.weight as evaluation_weight,
                ei.name as evaluation_name,
                ei.specific_weight,
                g.score
            FROM grades g
            JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
            JOIN evaluations e ON ei.evaluation_id = e.evaluation_id
            JOIN enrollments en ON g.enrollment_id = en.enrollment_id
            JOIN students st ON en.student_id = st.student_id
            JOIN sections s ON en.section_id = s.section_id
            JOIN course_instances ci ON s.instance_id = ci.instance_id
            WHERE ci.course_id = %s AND ci.instance_id = %s
            ORDER BY s.number, st.name, e.type, ei.name
        """, (course_id, instance_id))
        
        return self.cursor.fetchall()

    def get_section_grades(self, section_id):
        """Obtener todas las notas para una sección, incluyendo evaluaciones sin nota"""
        self.cursor.execute("""
            SELECT 
                s.student_id,
                s.name AS student_name,
                e.type AS evaluation_type,
                e.weight AS evaluation_weight,
                ei.name AS evaluation_name,
                ei.specific_weight,
                ei.instance_eval_id,
                g.score
            FROM enrollments en
            JOIN students s ON en.student_id = s.student_id
            JOIN evaluations e ON e.section_id = en.section_id
            JOIN evaluation_instances ei ON ei.evaluation_id = e.evaluation_id
            LEFT JOIN grades g ON g.instance_eval_id = ei.instance_eval_id AND g.enrollment_id = en.enrollment_id
            WHERE en.section_id = %s
            ORDER BY s.name, e.type, ei.name
        """, (section_id,))
        
        return self.cursor.fetchall()

    def get_course_info_for_grades(self, course_id, instance_id):
        """Obtener información del curso y la instancia para mostrar en la vista de notas"""
        self.cursor.execute("""
            SELECT 
                c.name as course_name,
                c.code as course_code,
                ci.year,
                ci.semester
            FROM courses c
            JOIN course_instances ci ON c.course_id = ci.course_id
            WHERE c.course_id = %s AND ci.instance_id = %s
        """, (course_id, instance_id))
        
        return self.cursor.fetchone()

    def create_or_update_grade(self, section_id: int, student_id: int, instance_eval_id: int, score: float):
        try:
            # Obtener enrollment_id
            self.cursor.execute("""
                SELECT enrollment_id FROM enrollments 
                WHERE section_id = %s AND student_id = %s
            """, (section_id, student_id))
            result = self.cursor.fetchone()
            if not result:
                return False, None, None
            enrollment_id = result['enrollment_id']

            # Revisar si la nota ya existe
            self.cursor.execute("""
                SELECT grade_id FROM grades 
                WHERE instance_eval_id = %s AND enrollment_id = %s
            """, (instance_eval_id, enrollment_id))
            exists = self.cursor.fetchone()

            if exists:
                # Update
                self.cursor.execute("""
                    UPDATE grades SET score = %s 
                    WHERE instance_eval_id = %s AND enrollment_id = %s
                """, (score, instance_eval_id, enrollment_id))
            else:
                # Insert
                self.cursor.execute("""
                    INSERT INTO grades (instance_eval_id, enrollment_id, score) 
                    VALUES (%s, %s, %s)
                """, (instance_eval_id, enrollment_id, score))

            self.db.commit()

            # Obtener pesos de evaluaciones del estudiante
            self.cursor.execute("""
                SELECT 
                    e.type AS eval_type,
                    e.weight AS eval_weight,
                    ei.specific_weight,
                    g.score
                FROM grades g
                JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
                JOIN evaluations e ON ei.evaluation_id = e.evaluation_id
                WHERE g.enrollment_id = %s
            """, (enrollment_id,))
            rows = self.cursor.fetchall()

            if not rows:
                return True, 0.0, 0.0

            # Calcular promedios por tipo y final
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

            return True, round(type_avgs.get(row['eval_type'], 0.0), 1), round(final_avg, 1)

        except Exception as e:
            print("Error al crear/actualizar nota:", e)
            return False, None, None
