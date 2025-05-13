import json
import re
from datetime import date
from app.db import DatabaseConnection

class JsonUploadService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def email_exists(self, email):
        self.cursor.execute("SELECT 1 FROM students WHERE email = %s", (email,))
        return self.cursor.fetchone() is not None

    def load_alumnos(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            # Validar que existe la clave "alumnos" y es una lista
            if "alumnos" not in raw_data or not isinstance(raw_data["alumnos"], list):
                return False, "El JSON debe contener una lista bajo la clave 'alumnos'."

            alumnos = raw_data["alumnos"]
            errores = []
            insertados = 0

            for i, alumno in enumerate(alumnos, start=1):
                try:
                    nombre = alumno.get("nombre")
                    correo = alumno.get("correo")
                    anio_ingreso = alumno.get("anio_ingreso")
                    id_ = alumno.get("id")  # Opcional

                    # Validaciones
                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError("Nombre inválido")

                    if not isinstance(correo, str) or "@" not in correo:
                        raise ValueError("Correo inválido")

                    if not isinstance(anio_ingreso, int):
                        raise ValueError("Año de ingreso debe ser un número entero")

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError("ID debe ser un entero o no estar presente")

                    if id_:
                        # Intentar insertar con ID si viene
                        self.cursor.execute("""
                            INSERT INTO students (student_id, name, email, admission_date)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email)
                        """, (id_, nombre, correo, f"{anio_ingreso}-01-01"))
                    else:
                        # Insertar sin ID (autoincremental)
                        self.cursor.execute("""
                            INSERT INTO students (name, email, admission_date)
                            VALUES (%s, %s, %s)
                        """, (nombre, correo, f"{anio_ingreso}-01-01"))

                    insertados += 1

                except Exception as e:
                    errores.append(f"Alumno #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertados} alumnos cargados. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertados} alumnos cargados exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            print("Error al cargar alumnos:", e)
            return False, "Error al procesar el archivo."