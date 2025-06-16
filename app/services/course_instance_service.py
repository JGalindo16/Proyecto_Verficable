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
    
    def get_enrolled_student_ids(self, section_id: int):
        self.cursor.execute("""
            SELECT student_id FROM enrollments WHERE section_id = %s
        """, (section_id,))
        result = self.cursor.fetchall()
        return [row['student_id'] for row in result]

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