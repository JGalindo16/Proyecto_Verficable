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
    
    def load_profesores(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if "profesores" not in raw_data or not isinstance(raw_data["profesores"], list):
                return False, "El JSON debe contener una lista bajo la clave 'profesores'."

            profesores = raw_data["profesores"]
            errores = []
            insertados = 0

            for i, prof in enumerate(profesores, start=1):
                try:
                    nombre = prof.get("nombre")
                    correo = prof.get("correo")
                    id_ = prof.get("id")  # Opcional

                    # Validaciones
                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError("Nombre inválido")

                    if not isinstance(correo, str) or not self.is_valid_email(correo):
                        raise ValueError("Correo inválido")

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError("ID debe ser un entero o no estar presente")

                    if id_:
                        self.cursor.execute("""
                            INSERT INTO professors (professor_id, name, email)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email)
                        """, (id_, nombre, correo))
                    else:
                        self.cursor.execute("""
                            INSERT INTO professors (name, email)
                            VALUES (%s, %s)
                        """, (nombre, correo))

                    insertados += 1

                except Exception as e:
                    errores.append(f"Profesor #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertados} profesores cargados. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertados} profesores cargados exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            print("Error al cargar profesores:", e)
            return False, "Error al procesar el archivo."

    def load_cursos(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if "cursos" not in raw_data or not isinstance(raw_data["cursos"], list):
                return False, "El JSON debe contener una lista bajo la clave 'cursos'."

            cursos = raw_data["cursos"]
            errores = []
            insertados = 0

            for i, curso in enumerate(cursos, start=1):
                try:
                    id_ = curso.get("id")
                    name = curso.get("descripcion")
                    codigo = curso.get("codigo")
                    creditos = curso.get("creditos", 0)
                    requisitos = curso.get("prerrequisitos", [])

                    if not isinstance(name, str) or not name.strip():
                        raise ValueError("Descripción inválida (campo 'name')")

                    if not isinstance(codigo, str) or not codigo.strip():
                        raise ValueError("Código inválido")

                    if not isinstance(creditos, int):
                        raise ValueError("Créditos inválidos (debe ser un entero)")

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError("ID inválido (debe ser entero o nulo)")

                    if not isinstance(requisitos, list):
                        raise ValueError("Los prerrequisitos deben ser una lista")

                    # Insertar curso
                    if id_:
                        self.cursor.execute("""
                            INSERT INTO courses (course_id, code, name, creditos)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE code = VALUES(code), name = VALUES(name), creditos = VALUES(creditos)
                        """, (id_, codigo, name, creditos))
                    else:
                        self.cursor.execute("""
                            INSERT INTO courses (code, name, creditos)
                            VALUES (%s, %s, %s)
                        """, (codigo, name, creditos))
                        id_ = self.cursor.lastrowid

                    # Prerrequisitos por código
                    for code in requisitos:
                        if not isinstance(code, str) or not code.strip():
                            raise ValueError("Código de prerrequisito inválido")

                        self.cursor.execute("SELECT course_id FROM courses WHERE code = %s", (code,))
                        result = self.cursor.fetchone()
                        if not result:
                            raise ValueError(f"El prerrequisito '{code}' no existe en la base de datos")

                        prereq_id = result['course_id']

                        self.cursor.execute("""
                            INSERT IGNORE INTO course_prerequisites (course_id, prerequisite_id)
                            VALUES (%s, %s)
                        """, (id_, prereq_id))

                    insertados += 1

                except Exception as e:
                    errores.append(f"Curso #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertados} cursos cargados. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertados} cursos cargados exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            print("Error al cargar cursos:", e)
            return False, "Error interno al procesar el archivo."

    def load_instancias(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            anio = raw_data.get("año")
            semestre = raw_data.get("semestre")
            instancias = raw_data.get("instancias", [])

            if not isinstance(anio, int):
                return False, "El campo 'año' debe ser un entero."

            if not isinstance(semestre, int) or semestre not in [1, 2]:
                return False, "El campo 'semestre' debe ser 1 o 2."

            if not isinstance(instancias, list):
                return False, "El campo 'instancias' debe ser una lista."

            errores = []
            insertados = 0
            for i, instancia in enumerate(instancias, start=1):
                try:
                    id_ = instancia.get("id")
                    curso_id = instancia.get("curso_id")

                    if not isinstance(curso_id, int):
                        raise ValueError("El campo 'curso_id' debe ser un entero.")

                    self.cursor.execute("SELECT 1 FROM courses WHERE course_id = %s", (curso_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(f"El curso_id {curso_id} no existe.")

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError("El campo 'id' debe ser entero o no estar presente.")

                    if id_:
                        self.cursor.execute("""
                            INSERT INTO course_instances (instance_id, course_id, year, semester)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE course_id=VALUES(course_id), year=VALUES(year), semester=VALUES(semester)
                        """, (id_, curso_id, anio, str(semestre)))
                    else:
                        self.cursor.execute("""
                            INSERT INTO course_instances (course_id, year, semester)
                            VALUES (%s, %s, %s)
                        """, (curso_id, anio, str(semestre)))

                    insertados += 1
                except Exception as e:
                    errores.append(f"Instancia #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertados} instancias cargadas. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertados} instancias cargadas exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            print("Error al cargar instancias:", e)
            return False, "Error interno al procesar el archivo."

    def load_enrollments(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if "alumnos_seccion" not in raw_data or not isinstance(raw_data["alumnos_seccion"], list):
                return False, "El JSON debe contener una lista bajo la clave 'alumnos_seccion'."

            inscripciones = raw_data["alumnos_seccion"]
            errores = []
            insertados = 0

            for i, inscripcion in enumerate(inscripciones, start=1):
                try:
                    seccion_id = inscripcion.get("seccion_id")
                    alumno_id = inscripcion.get("alumno_id")

                    if not isinstance(seccion_id, int) or not isinstance(alumno_id, int):
                        raise ValueError("IDs inválidos (deben ser enteros)")

                    # Verificar existencia de section
                    self.cursor.execute("SELECT 1 FROM sections WHERE section_id = %s", (seccion_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(f"La sección con ID {seccion_id} no existe")

                    # Verificar existencia de student
                    self.cursor.execute("SELECT 1 FROM students WHERE student_id = %s", (alumno_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(f"El alumno con ID {alumno_id} no existe")

                    # Insertar inscripción
                    self.cursor.execute("""
                        INSERT INTO enrollments (student_id, section_id)
                        VALUES (%s, %s)
                    """, (alumno_id, seccion_id))

                    insertados += 1

                except Exception as e:
                    errores.append(f"Ingreso #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertados} inscripciones cargadas. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertados} inscripciones cargadas exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            print("Error al cargar inscripciones:", e)
            return False, "Error interno al procesar el archivo."

    def load_classrooms(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if "salas" not in raw_data or not isinstance(raw_data["salas"], list):
                return False, "El JSON debe contener una lista bajo la clave 'salas'."

            salas = raw_data["salas"]
            errores = []
            insertados = 0

            for i, sala in enumerate(salas, start=1):
                try:
                    id_ = sala.get("id")
                    nombre = sala.get("nombre")
                    capacidad = sala.get("capacidad")

                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError("Nombre inválido")

                    if not isinstance(capacidad, int) or capacidad <= 0:
                        raise ValueError("Capacidad inválida (debe ser un número entero positivo)")

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError("ID inválido (debe ser entero o nulo)")

                    if id_:
                        self.cursor.execute("""
                            INSERT INTO classrooms (classroom_id, name, capacity)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE name = VALUES(name), capacity = VALUES(capacity)
                        """, (id_, nombre, capacidad))
                    else:
                        self.cursor.execute("""
                            INSERT INTO classrooms (name, capacity)
                            VALUES (%s, %s)
                        """, (nombre, capacidad))

                    insertados += 1

                except Exception as e:
                    errores.append(f"Sala #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertados} salas cargadas. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertados} salas cargadas exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            print("Error al cargar salas:", e)
            return False, "Error interno al procesar el archivo."

    def load_instancias_con_secciones(self, file_storage):
        try:
            data = json.load(file_storage)

            if "secciones" not in data or not isinstance(data["secciones"], list):
                return False, "El JSON debe contener una lista bajo la clave 'secciones'."

            secciones = data["secciones"]
            insertadas = 0
            errores = []

            def round_with_correction(values):
                rounded = [round(v, 2) for v in values]
                diff = round(1.0 - sum(rounded), 2)
                if rounded:
                    rounded[-1] += diff
                return rounded

            for i, seccion in enumerate(secciones, start=1):
                try:
                    instance_id = int(seccion.get("instancia_curso"))
                    numero = int(seccion.get("id"))
                    profesor_id = int(seccion.get("profesor_id"))

                    # Verificaciones
                    self.cursor.execute("SELECT 1 FROM course_instances WHERE instance_id = %s", (instance_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(f"Instancia con ID {instance_id} no existe")

                    self.cursor.execute("SELECT 1 FROM professors WHERE professor_id = %s", (profesor_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(f"Profesor con ID {profesor_id} no existe")

                    self.cursor.execute("""
                        INSERT INTO sections (instance_id, number, professor_id)
                        VALUES (%s, %s, %s)
                    """, (instance_id, numero, profesor_id))
                    section_id = self.cursor.lastrowid

                    evaluacion = seccion.get("evaluacion")
                    if evaluacion:
                        tipo_eval = evaluacion.get("tipo")
                        if tipo_eval not in ("peso", "porcentaje"):
                            raise ValueError(f"Tipo de evaluación inválido: {tipo_eval}")

                        combinacion = evaluacion.get("combinacion_topicos", [])
                        topicos = evaluacion.get("topicos", {})

                        valores_topico = [float(t["valor"]) for t in combinacion]
                        if tipo_eval == "peso":
                            total = sum(valores_topico)
                            pesos_relativos = round_with_correction([v / total for v in valores_topico])
                        else:
                            pesos_relativos = round_with_correction([v / 100 for v in valores_topico])

                        for idx, topico_meta in enumerate(combinacion):
                            topico_id = str(topico_meta.get("id"))
                            nombre = topico_meta.get("nombre")
                            peso_normalizado = pesos_relativos[idx]

                            if topico_id not in topicos:
                                raise ValueError(f"No hay descripción para el tópico con id {topico_id}")

                            self.cursor.execute("""
                                INSERT INTO evaluations (section_id, type, weight, optional)
                                VALUES (%s, %s, %s, %s)
                            """, (section_id, nombre, peso_normalizado, False))
                            evaluation_id = self.cursor.lastrowid

                            topico = topicos[topico_id]
                            cantidad = topico.get("cantidad")
                            valores = topico.get("valores", [])
                            obligatorias = topico.get("obligatorias", [])

                            if cantidad != len(valores) or cantidad != len(obligatorias):
                                raise ValueError(f"Tópico {topico_id} tiene cantidades inconsistentes.")

                            if topico["tipo"] == "peso":
                                total = sum(valores)
                                instancias_pesos = round_with_correction([v / total for v in valores])
                            else:
                                instancias_pesos = round_with_correction([v / 100 for v in valores])

                            for j in range(cantidad):
                                self.cursor.execute("""
                                    INSERT INTO evaluation_instances (evaluation_id, name, specific_weight, mandatory)
                                    VALUES (%s, %s, %s, %s)
                                """, (
                                    evaluation_id,
                                    f"{nombre} Instancia {j + 1}",
                                    instancias_pesos[j],
                                    obligatorias[j]
                                ))

                    insertadas += 1

                except Exception as e:
                    errores.append(f"Sección #{i}: {str(e)}")

            self.db.commit()

            if errores:
                return False, f"{insertadas} secciones cargadas con éxito. {len(errores)} errores.\n" + "\n".join(errores)
            return True, f"{insertadas} secciones cargadas exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            print("Error en carga de secciones:", e)
            return False, "Error interno al procesar el archivo."

    def load_notas(self, file_storage):
        try:
            data = json.load(file_storage)

            if "notas" not in data or not isinstance(data["notas"], list):
                return False, "El JSON debe contener una lista bajo la clave 'notas'."

            notas = data["notas"]
            insertadas = 0
            errores = []

            for i, nota_data in enumerate(notas, start=1):
                try:
                    required_fields = ["alumno_id", "topico_id", "instancia", "nota"]
                    for field in required_fields:
                        if nota_data.get(field) is None:
                            raise ValueError(f"Campo '{field}' faltante o nulo")

                    alumno_id = int(nota_data["alumno_id"])
                    topico_id = int(nota_data["topico_id"])
                    instancia = int(nota_data["instancia"])
                    nota = float(nota_data["nota"])

                    if not (1.0 <= nota <= 7.0):
                        raise ValueError("La nota debe estar entre 1.0 y 7.0.")

                    # Verificar que el alumno exista
                    self.cursor.execute("SELECT 1 FROM students WHERE student_id = %s", (alumno_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(f"Alumno con ID {alumno_id} no existe")

                    # Verificar que exista la instancia de evaluación
                    self.cursor.execute("""
                        SELECT ei.instance_eval_id, e.section_id
                        FROM evaluation_instances ei
                        JOIN evaluations e ON ei.evaluation_id = e.evaluation_id
                        WHERE e.evaluation_id = %s AND ei.name LIKE %s
                    """, (topico_id, f"%Instancia {instancia}"))
                    result = self.cursor.fetchone()
                    if not result:
                        raise ValueError(f"No existe la instancia {instancia} para el tópico {topico_id}")

                    instance_eval_id = result["instance_eval_id"]
                    section_id = result["section_id"]

                    # Verificar si el alumno está inscrito en la sección correspondiente
                    self.cursor.execute("""
                        SELECT enrollment_id FROM enrollments
                        WHERE student_id = %s AND section_id = %s
                    """, (alumno_id, section_id))
                    result = self.cursor.fetchone()
                    if not result:
                        raise ValueError(f"El alumno {alumno_id} no está inscrito en la sección {section_id}")
                    
                    enrollment_id = result["enrollment_id"]

                    # Insertar la nota
                    self.cursor.execute("""
                        INSERT INTO grades (enrollment_id, instance_eval_id, score)
                        VALUES (%s, %s, %s)
                    """, (enrollment_id, instance_eval_id, nota))

                    insertadas += 1

                except Exception as e:
                    errores.append(f"Nota #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertadas} notas cargadas con éxito. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertadas} notas cargadas exitosamente."

        except json.JSONDecodeError:
            return False, "El archivo no es un JSON válido."
        except Exception as e:
            return False, "Error interno al procesar el archivo."