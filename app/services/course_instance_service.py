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
            # Convertir a número entero, ya que ahora es un campo numérico
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
            # Primero eliminamos todas las inscripciones actuales
            self.cursor.execute("DELETE FROM enrollments WHERE section_id = %s", (section_id,))
            
            # Luego agregamos las nuevas inscripciones
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