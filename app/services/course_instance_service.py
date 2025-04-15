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
    
    