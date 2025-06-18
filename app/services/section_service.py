from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
from app.sql_queries.section_queries import *

class SectionService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def get_sections_by_instance(self, instance_id: int):
        self.cursor.execute(GET_SECTIONS_BY_INSTANCE, (instance_id,))
        return self.cursor.fetchall()

    def add_section(self, instance_id: int, section_name: str, professor_id: int, student_ids: list = None):
        try:
            section_number = int(section_name)

            print(student_ids)
            self.cursor.execute(CHECK_DUPLICATE_SECTION_IN_INSTANCE, (instance_id, section_number))
            if self.cursor.fetchone()['count'] > 0:
                return {"success": False, "message": "Ya existe una sección con ese número en esta instancia."}


            if student_ids is None:
                student_ids = []

            for student_id in student_ids:
                self.cursor.execute(CHECK_STUDENT_ALREADY_ENROLLED_WITH_NAME, (student_id, instance_id, 0))
                result_check = self.cursor.fetchone()
                if result_check:
                    return {
                        "success": False,
                        "message": f"El estudiante \"{result_check['name']}\" ya está inscrito en otra sección de esta instancia."
                    }

            self.cursor.execute(INSERT_SECTION, (instance_id, section_number, professor_id))
            section_id = self.cursor.lastrowid

            if student_ids:
                values = [(section_id, student_id) for student_id in student_ids]
                self.cursor.executemany(INSERT_STUDENTS_TO_SECTION, values)

            self.db.commit()
            return {
                "success": True,
                "message": "Sección y estudiantes creados correctamente.",
                "section_id": section_id
            }

        except Exception as e:
            return {"success": False, "message": "Error al agregar sección."}

    def add_students_to_section(self, section_id: int, student_ids: list):
        try:
            self.cursor.execute(GET_INSTANCE_ID_FROM_SECTION, (section_id,))
            result = self.cursor.fetchone()
            if not result:
                return {"success": False, "message": "Sección no encontrada."}
            instance_id = result["instance_id"]

            for student_id in student_ids:
                self.cursor.execute(CHECK_STUDENT_ALREADY_ENROLLED, (student_id, instance_id, section_id))
                if self.cursor.fetchone()["count"] > 0:
                    return {
                        "success": False,
                        "message": f"El estudiante con ID {student_id} ya está inscrito en otra sección de esta instancia."
                    }

            values = [(section_id, student_id) for student_id in student_ids]
            self.cursor.executemany(INSERT_STUDENTS_TO_SECTION, values)
            self.db.commit()
            return {"success": True, "message": "Estudiantes agregados correctamente."}
        except Exception as e:
            return {"success": False, "message": "Error al agregar estudiantes a la sección."}

    def delete_section(self, section_id: int):
        try:
            self.cursor.execute(DELETE_SECTION, (section_id,))
            self.db.commit()
            return {"success": True, "message": "Sección eliminada exitosamente."}
        except Exception as e:
            return {"success": False, "message": "Error al eliminar sección."}

    def get_section_by_id(self, section_id: int):
        self.cursor.execute(GET_SECTION_BY_ID, (section_id,))
        return self.cursor.fetchone()

    def get_students_in_section(self, section_id: int):
        self.cursor.execute(GET_STUDENTS_IN_SECTION, (section_id,))
        return self.cursor.fetchall()

    def update_section(self, section_id: int, section_number: int, professor_id: int):
        try:
            self.cursor.execute(GET_INSTANCE_ID_FROM_SECTION, (section_id,))
            result = self.cursor.fetchone()
            if not result:
                return {"success": False, "message": "Sección no encontrada."}
            instance_id = result["instance_id"]
            
            self.cursor.execute(CHECK_DUPLICATE_SECTION_IN_INSTANCE, (instance_id, section_number))
            existing_section = self.cursor.fetchone()
            if existing_section and existing_section["count"] > 0:
                self.cursor.execute("SELECT section_id FROM sections WHERE instance_id = %s AND number = %s", (instance_id, section_number))
                existing_section_data = self.cursor.fetchone()
                if existing_section_data and existing_section_data["section_id"] != section_id:
                    return {"success": False, "message": "Ya existe otra sección con ese número en esta instancia."}

            self.cursor.execute(UPDATE_SECTION, (section_number, professor_id, section_id))
            self.db.commit()
            return {"success": True, "message": "Sección actualizada exitosamente."}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error al actualizar sección: {str(e)}"}

    def update_section_students(self, section_id: int, student_ids: list):
        try:
            self.cursor.execute(GET_INSTANCE_ID_FROM_SECTION, (section_id,))
            result = self.cursor.fetchone()
            if not result:
                return {"success": False, "message": "Sección no encontrada."}
            instance_id = result["instance_id"]

            for student_id in student_ids:
                self.cursor.execute(CHECK_STUDENT_ALREADY_ENROLLED_WITH_NAME, (student_id, instance_id, section_id))
                result_check = self.cursor.fetchone()
                if result_check:
                    return {
                        "success": False,
                        "message": f"El estudiante \"{result_check['name']}\" ya está inscrito en otra sección de esta instancia."
                    }

            self.cursor.execute(DELETE_STUDENTS_FROM_SECTION, (section_id,))
            if student_ids:
                values = [(section_id, student_id) for student_id in student_ids]
                self.cursor.executemany(INSERT_STUDENTS_TO_SECTION, values)
            self.db.commit()
            return {"success": True, "message": "Estudiantes actualizados correctamente."}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error al actualizar estudiantes: {str(e)}"}

    def get_enrolled_student_ids(self, section_id: int):
        self.cursor.execute(GET_ENROLLED_STUDENT_IDS, (section_id,))
        result = self.cursor.fetchall()
        return [row['student_id'] for row in result]

    def get_all_professors(self):
        self.cursor.execute(GET_ALL_PROFESSORS)
        return self.cursor.fetchall()

    def get_all_students(self):
        self.cursor.execute(GET_ALL_STUDENTS)
        return self.cursor.fetchall()
    
    def check_student_enrollment_in_instance(self, student_id: int, instance_id: int, current_section_id: int = 0):
        self.cursor.execute(CHECK_STUDENT_ALREADY_ENROLLED_WITH_NAME, (student_id, instance_id, current_section_id))
        return self.cursor.fetchone()