from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST

class CourseInstanceService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def add_instance(self, course_id: int, year: int, semester: str):
        try:
            sql = "INSERT INTO course_instances (course_id, year, semester) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (course_id, year, semester))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al insertar instancia:", e)
            return HTTP_BAD_REQUEST

    def get_instances_by_course(self, course_id: int):
        self.cursor.execute("""
            SELECT instance_id AS id, year, semester
            FROM course_instances
            WHERE course_id = %s
        """, (course_id,))
        return self.cursor.fetchall()

    def delete_instance(self, instance_id: int):
        try:
            sql = "DELETE FROM course_instances WHERE instance_id = %s"
            self.cursor.execute(sql, (instance_id,))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al eliminar instancia:", e)
            return HTTP_BAD_REQUEST
        
    def update_instance(self, instance_id: int, year: int, semester: str):
        try:
            sql = "UPDATE course_instances SET year = %s, semester = %s WHERE instance_id = %s"
            self.cursor.execute(sql, (year, semester, instance_id))
            self.db.commit()
            return HTTP_OK
        except Exception as e:
            print("Error al actualizar instancia:", e)
            return HTTP_BAD_REQUEST
    
    def get_instance_by_id(self, instance_id: int):
        self.cursor.execute("""
            SELECT instance_id AS id, course_id, year, semester
            FROM course_instances
            WHERE instance_id = %s
        """, (instance_id,))
        return self.cursor.fetchone()
    
    def get_sections_by_instance(self, instance_id: int):
        self.cursor.execute("""
            SELECT 
                s.section_id AS id,
                s.number,
                s.professor_id,
                CONCAT('Sección ', s.number) AS name,
                p.name AS professor,
                COUNT(e.enrollment_id) AS student_count
            FROM sections s
            LEFT JOIN professors p ON s.professor_id = p.professor_id
            LEFT JOIN enrollments e ON s.section_id = e.section_id
            WHERE s.instance_id = %s
            GROUP BY s.section_id, p.name
        """, (instance_id,))
        return self.cursor.fetchall()
    
    def add_section(self, instance_id: int, section_name: str, professor_id: int):
        try:
            section_number = int(section_name)
            
            sql = "INSERT INTO sections (instance_id, number, professor_id) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (instance_id, section_number, professor_id))
            self.db.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print("Error al agregar sección:", e)
            return None
        
    def add_students_to_section(self, section_id: int, student_ids: list):
        try:
            sql = "INSERT INTO enrollments (section_id, student_id) VALUES (%s, %s)"
            values = [(section_id, student_id) for student_id in student_ids]
            self.cursor.executemany(sql, values)
            self.db.commit()
        except Exception as e:
            print("Error al agregar estudiantes a la sección:", e)
    
    def get_all_professors(self):
        self.cursor.execute("SELECT professor_id AS id, name FROM professors")
        return self.cursor.fetchall()

    def get_all_students(self):
        self.cursor.execute("SELECT student_id AS id, name FROM students")
        return self.cursor.fetchall()
    
    def delete_section(self, section_id: int):
        try:
            sql = "DELETE FROM sections WHERE section_id = %s"
            self.cursor.execute(sql, (section_id,))
            self.db.commit()
            return True
        except Exception as e:
            print("Error al eliminar sección:", e)
            return False

    def get_section_by_id(self, section_id: int):
        self.cursor.execute("""
            SELECT 
                s.section_id AS id,
                s.number,
                s.professor_id,
                p.name AS professor_name,
                CONCAT('Sección ', s.number) AS name
            FROM sections s
            LEFT JOIN professors p ON s.professor_id = p.professor_id
            WHERE s.section_id = %s
        """, (section_id,))
        return self.cursor.fetchone()
    
    def get_students_in_section(self, section_id: int):
        self.cursor.execute("""
            SELECT 
                s.student_id AS id,
                s.name,
                s.email
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            WHERE e.section_id = %s
            ORDER BY s.name
        """, (section_id,))
        return self.cursor.fetchall()
        
    def update_section(self, section_id: int, section_number: int, professor_id: int):
        try:
            sql = "UPDATE sections SET number = %s, professor_id = %s WHERE section_id = %s"
            self.cursor.execute(sql, (section_number, professor_id, section_id))
            self.db.commit()
            return True
        except Exception as e:
            print("Error al actualizar sección:", e)
            return False
            
    def update_section_students(self, section_id: int, student_ids: list):
        try:
            self.cursor.execute("DELETE FROM enrollments WHERE section_id = %s", (section_id,))
            
            if student_ids:
                sql = "INSERT INTO enrollments (section_id, student_id) VALUES (%s, %s)"
                values = [(section_id, student_id) for student_id in student_ids]
                self.cursor.executemany(sql, values)
                
            self.db.commit()
            return True
        except Exception as e:
            print("Error al actualizar estudiantes de la sección:", e)
            return False
            
    def get_enrolled_student_ids(self, section_id: int):
        self.cursor.execute("""
            SELECT student_id FROM enrollments WHERE section_id = %s
        """, (section_id,))
        result = self.cursor.fetchall()
        return [row['student_id'] for row in result]

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
    
    def validate_evaluation_weights(self, evaluation_id):
        """
        Valida que la suma de los specific_weight de las evaluation_instances 
        para un evaluation_id específico sea 100%
        """
        self.cursor.execute("""
            SELECT SUM(specific_weight) as total_weight
            FROM evaluation_instances
            WHERE evaluation_id = %s
        """, (evaluation_id,))
        
        result = self.cursor.fetchone()
        total_weight = result['total_weight'] if result['total_weight'] else 0
        
        return abs(total_weight - 100) < 0.01 
    
    def get_current_weights_for_evaluation(self, evaluation_id):
        """
        Obtiene todas las instancias y sus pesos para una evaluación específica
        """
        self.cursor.execute("""
            SELECT instance_eval_id, name, specific_weight
            FROM evaluation_instances
            WHERE evaluation_id = %s
        """, (evaluation_id,))
        
        return self.cursor.fetchall()
    
    def add_evaluation_instance(self, evaluation_id, name, specific_weight, mandatory=True):
        self.cursor.execute("""
            SELECT SUM(specific_weight) as total_weight
            FROM evaluation_instances
            WHERE evaluation_id = %s
        """, (evaluation_id,))
        
        result = self.cursor.fetchone()
        current_weight = result['total_weight'] if result['total_weight'] else 0
        
        if current_weight + specific_weight > 100.01:  
            return {"success": False, "message": "La suma de los pesos excede el 100%"}
        
        try:
            sql = """
                INSERT INTO evaluation_instances 
                (evaluation_id, name, specific_weight, mandatory) 
                VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql, (evaluation_id, name, specific_weight, mandatory))
            self.db.commit()
            return {"success": True, "id": self.cursor.lastrowid}
        except Exception as e:
            print("Error al insertar instancia de evaluación:", e)
            return {"success": False, "message": str(e)}
    
    def update_evaluation_instance(self, instance_eval_id, name, specific_weight, mandatory=None):
        """Actualiza una instancia de evaluación existente y verifica los pesos"""
        try:
            self.cursor.execute("""
                SELECT evaluation_id, specific_weight
                FROM evaluation_instances
                WHERE instance_eval_id = %s
            """, (instance_eval_id,))
            current = self.cursor.fetchone()
            
            if not current:
                return {"success": False, "message": "Instancia de evaluación no encontrada"}
            
            evaluation_id = current['evaluation_id']
            old_weight = current['specific_weight']
            
            self.cursor.execute("""
                SELECT SUM(specific_weight) as total_weight
                FROM evaluation_instances
                WHERE evaluation_id = %s AND instance_eval_id != %s
            """, (evaluation_id, instance_eval_id))
            
            result = self.cursor.fetchone()
            other_weights = result['total_weight'] if result and result['total_weight'] else 0
            
            if other_weights + specific_weight > 1.001: 
                return {
                    "success": False, 
                    "message": f"La suma de los pesos específicos excedería el 100%. Otros: {other_weights*100}%, Nuevo: {specific_weight*100}%"
                }
            
            sql = "UPDATE evaluation_instances SET name = %s, specific_weight = %s"
            params = [name, specific_weight]
            
            if mandatory is not None:
                sql += ", mandatory = %s"
                params.append(mandatory)
                
            sql += " WHERE instance_eval_id = %s"
            params.append(instance_eval_id)
            
            self.cursor.execute(sql, tuple(params))
            self.db.commit()
            return {"success": True}
            
        except Exception as e:
            print("Error al actualizar instancia de evaluación:", e)
            return {"success": False, "message": str(e)}
        
    def redistribute_weights_after_delete(self, evaluation_id):
        """Redistribuye los pesos de las instancias restantes tras eliminar una"""
        try:
            self.cursor.execute("""
                SELECT COUNT(*) as count
                FROM evaluation_instances
                WHERE evaluation_id = %s
            """, (evaluation_id,))
            
            count = self.cursor.fetchone()['count']
            
            if count == 0:
                return {"success": True, "message": "No hay instancias que actualizar"}
            
            new_weight = 1.0 / count
            
            self.cursor.execute("""
                UPDATE evaluation_instances
                SET specific_weight = %s
                WHERE evaluation_id = %s
            """, (new_weight, evaluation_id))
            
            self.db.commit()
            return {"success": True}
            
        except Exception as e:
            print("Error al redistribuir pesos:", e)
            return {"success": False, "message": str(e)}

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