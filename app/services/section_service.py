from app.db import DatabaseConnection
from app.http_errors import HTTP_OK, HTTP_BAD_REQUEST
from app.sql_queries.section_queries import *


class SectionService:
    """Service for managing sections and student enrollments."""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def get_sections_by_instance(self, instance_id: int):
        self.cursor.execute(GET_SECTIONS_BY_INSTANCE, (instance_id,))
        return self.cursor.fetchall()

    def _check_duplicate_section(self, instance_id: int, section_number: int):
        self.cursor.execute(
            CHECK_DUPLICATE_SECTION_IN_INSTANCE, (instance_id, section_number)
        )
        result = self.cursor.fetchone()
        return result['count'] > 0 if result else False

    def _check_student_enrollment_conflicts(self, student_ids: list, 
                                          instance_id: int, 
                                          exclude_section_id: int = 0):
        for student_id in student_ids:
            self.cursor.execute(
                CHECK_STUDENT_ALREADY_ENROLLED_WITH_NAME,
                (student_id, instance_id, exclude_section_id)
            )
            result = self.cursor.fetchone()
            if result:
                return result
        return None

    def _get_instance_id_from_section(self, section_id: int):
        self.cursor.execute(GET_INSTANCE_ID_FROM_SECTION, (section_id,))
        result = self.cursor.fetchone()
        return result["instance_id"] if result else None

    def _create_section(self, instance_id: int, section_number: int, 
                       professor_id: int):
        self.cursor.execute(
            INSERT_SECTION, (instance_id, section_number, professor_id)
        )
        return self.cursor.lastrowid

    def _enroll_students_in_section(self, section_id: int, student_ids: list):
        if student_ids:
            values = [(section_id, student_id) for student_id in student_ids]
            self.cursor.executemany(INSERT_STUDENTS_TO_SECTION, values)

    def add_section(self, instance_id: int, section_name: str, 
                   professor_id: int, student_ids: list = None):
        """Add a new section with optional student enrollment."""
        try:
            section_number = int(section_name)
            
            if student_ids is None:
                student_ids = []

            if self._check_duplicate_section(instance_id, section_number):
                return {
                    "success": False, 
                    "message": "Ya existe una sección con ese número en esta "
                              "instancia."
                }

            conflict = self._check_student_enrollment_conflicts(
                student_ids, instance_id
            )
            if conflict:
                return {
                    "success": False,
                    "message": f"El estudiante \"{conflict['name']}\" ya está "
                              f"inscrito en otra sección de esta instancia."
                }

            section_id = self._create_section(
                instance_id, section_number, professor_id
            )

            self._enroll_students_in_section(section_id, student_ids)

            self.db.commit()
            
            return {
                "success": True,
                "message": "Sección y estudiantes creados correctamente.",
                "section_id": section_id
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False, 
                "message": "Error al agregar sección."
            }

    def add_students_to_section(self, section_id: int, student_ids: list):
        try:
            instance_id = self._get_instance_id_from_section(section_id)
            if not instance_id:
                return {
                    "success": False, 
                    "message": "Sección no encontrada."
                }

            conflict = self._check_student_enrollment_conflicts(
                student_ids, instance_id, section_id
            )
            if conflict:
                return {
                    "success": False,
                    "message": f"El estudiante \"{conflict['name']}\" ya está "
                              f"inscrito en otra sección de esta instancia."
                }

            self._enroll_students_in_section(section_id, student_ids)

            self.db.commit()
            
            return {
                "success": True, 
                "message": "Estudiantes agregados correctamente."
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False, 
                "message": "Error al agregar estudiantes a la sección."
            }

    def delete_section(self, section_id: int):
        try:
            self.cursor.execute(DELETE_SECTION, (section_id,))
            self.db.commit()
            return {
                "success": True, 
                "message": "Sección eliminada exitosamente."
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False, 
                "message": "Error al eliminar sección."
            }

    def get_section_by_id(self, section_id: int):
        self.cursor.execute(GET_SECTION_BY_ID, (section_id,))
        return self.cursor.fetchone()

    def get_students_in_section(self, section_id: int):
        self.cursor.execute(GET_STUDENTS_IN_SECTION, (section_id,))
        return self.cursor.fetchall()

    def update_section(self, section_id: int, section_number: int, 
                      professor_id: int):
        try:
            instance_id = self._get_instance_id_from_section(section_id)
            if not instance_id:
                return {
                    "success": False, 
                    "message": "Sección no encontrada."
                }
            
            self.cursor.execute(
                CHECK_DUPLICATE_SECTION_IN_INSTANCE, 
                (instance_id, section_number)
            )
            existing_section = self.cursor.fetchone()
            if existing_section and existing_section["count"] > 0:
                self.cursor.execute(
                    "SELECT section_id FROM sections WHERE instance_id = %s "
                    "AND number = %s", 
                    (instance_id, section_number)
                )
                existing_section_data = self.cursor.fetchone()
                if (existing_section_data and 
                    existing_section_data["section_id"] != section_id):
                    return {
                        "success": False, 
                        "message": "Ya existe otra sección con ese número en "
                                  "esta instancia."
                    }

            self.cursor.execute(
                UPDATE_SECTION, (section_number, professor_id, section_id)
            )
            self.db.commit()
            
            return {
                "success": True, 
                "message": "Sección actualizada exitosamente."
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False, 
                "message": f"Error al actualizar sección: {str(e)}"
            }

    def update_section_students(self, section_id: int, student_ids: list):
        try:
            instance_id = self._get_instance_id_from_section(section_id)
            if not instance_id:
                return {
                    "success": False, 
                    "message": "Sección no encontrada."
                }

            conflict = self._check_student_enrollment_conflicts(
                student_ids, instance_id, section_id
            )
            if conflict:
                return {
                    "success": False,
                    "message": f"El estudiante \"{conflict['name']}\" ya está "
                              f"inscrito en otra sección de esta instancia."
                }

            self.cursor.execute(DELETE_STUDENTS_FROM_SECTION, (section_id,))
            
            self._enroll_students_in_section(section_id, student_ids)
            
            self.db.commit()
            
            return {
                "success": True, 
                "message": "Estudiantes actualizados correctamente."
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False, 
                "message": f"Error al actualizar estudiantes: {str(e)}"
            }

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
    
    def check_student_enrollment_in_instance(self, student_id: int, 
                                           instance_id: int, 
                                           current_section_id: int = 0):
        self.cursor.execute(
            CHECK_STUDENT_ALREADY_ENROLLED_WITH_NAME, 
            (student_id, instance_id, current_section_id)
        )
        return self.cursor.fetchone()