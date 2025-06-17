import json
import re
from datetime import date
from app.db import DatabaseConnection

class JsonUploadService:
    # Límites y constantes
    _MAX_ITEMS = 100
    
    # Patrones de validación
    _EMAIL_PATTERN = r"[^@]+@[^@]+\.[^@]+"
    
    # Claves JSON
    _KEY_ALUMNOS = "alumnos"
    _KEY_PROFESORES = "profesores"
    _KEY_CURSOS = "cursos"
    _KEY_INSTANCIAS = "instancias"
    _KEY_ALUMNOS_SECCION = "alumnos_seccion"
    _KEY_SALAS = "salas"
    _KEY_SECCIONES = "secciones"
    _KEY_NOTAS = "notas"
    _KEY_EVALUACION = "evaluacion"
    _KEY_TOPICOS = "topicos"
    _KEY_COMBINACION_TOPICOS = "combinacion_topicos"
    
    # Campos de datos
    _FIELD_NOMBRE = "nombre"
    _FIELD_CORREO = "correo"
    _FIELD_ANIO_INGRESO = "anio_ingreso"
    _FIELD_ID = "id"
    _FIELD_DESCRIPCION = "descripcion"
    _FIELD_CODIGO = "codigo"
    _FIELD_CREDITOS = "creditos"
    _FIELD_PRERREQUISITOS = "prerrequisitos"
    _FIELD_ANO = "año"
    _FIELD_SEMESTRE = "semestre"
    _FIELD_CURSO_ID = "curso_id"
    _FIELD_SECCION_ID = "seccion_id"
    _FIELD_ALUMNO_ID = "alumno_id"
    _FIELD_CAPACIDAD = "capacidad"
    _FIELD_INSTANCIA_CURSO = "instancia_curso"
    _FIELD_PROFESOR_ID = "profesor_id"
    _FIELD_TOPICO_ID = "topico_id"
    _FIELD_INSTANCIA = "instancia"
    _FIELD_NOTA = "nota"
    _FIELD_TIPO = "tipo"
    _FIELD_VALOR = "valor"
    _FIELD_CANTIDAD = "cantidad"
    _FIELD_VALORES = "valores"
    _FIELD_OBLIGATORIAS = "obligatorias"
    
    # Tipos de evaluación
    _EVAL_TYPE_PESO = "peso"
    _EVAL_TYPE_PORCENTAJE = "porcentaje"
    
    # Rangos de valores
    _MIN_GRADE = 1.0
    _MAX_GRADE = 7.0
    _MIN_SEMESTER = 1
    _MAX_SEMESTER = 2
    
    # Mensajes de error
    _MSG_NO_JSON_KEY = "El JSON debe contener una lista bajo la clave '{key}'."
    _MSG_INVALID_JSON = "El archivo no es un JSON válido."
    _MSG_PROCESSING_ERROR = "Error al procesar el archivo."
    _MSG_INTERNAL_ERROR = "Error interno al procesar el archivo."
    _MSG_INVALID_NAME = "Nombre inválido"
    _MSG_INVALID_EMAIL = "Correo inválido"
    _MSG_INVALID_YEAR = "Año de ingreso debe ser un número entero"
    _MSG_INVALID_ID = "ID debe ser un entero o no estar presente"
    _MSG_INVALID_CODE = "Código inválido"
    _MSG_INVALID_CREDITS = "Créditos inválidos (debe ser un entero)"
    _MSG_INVALID_PREREQ = "Los prerrequisitos deben ser una lista"
    _MSG_INVALID_CAPACITY = "Capacidad inválida (debe ser un número entero positivo)"
    _MSG_COURSE_NOT_EXISTS = "El curso_id {id} no existe."
    _MSG_STUDENT_NOT_EXISTS = "El alumno con ID {id} no existe"
    _MSG_SECTION_NOT_EXISTS = "La sección con ID {id} no existe"
    _MSG_GRADE_RANGE = f"La nota debe estar entre {_MIN_GRADE} y {_MAX_GRADE}."
    
    # Formato de fecha
    _DATE_FORMAT = "{year}-01-01"
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def is_valid_email(self, email):
        return re.match(self._EMAIL_PATTERN, email)

    def email_exists(self, email):
        self.cursor.execute("SELECT 1 FROM students WHERE email = %s", (email,))
        return self.cursor.fetchone() is not None

    def load_alumnos(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            # Validar que existe la clave "alumnos" y es una lista
            if self._KEY_ALUMNOS not in raw_data or not isinstance(raw_data[self._KEY_ALUMNOS], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_ALUMNOS)

            alumnos = raw_data[self._KEY_ALUMNOS]
            
            # Validar tamaño máximo
            if len(alumnos) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(alumnos)} alumnos. Máximo permitido: {self._MAX_ITEMS}."
            
            errores = []
            insertados = 0

            for i, alumno in enumerate(alumnos, start=1):
                try:
                    nombre = alumno.get(self._FIELD_NOMBRE)
                    correo = alumno.get(self._FIELD_CORREO)
                    anio_ingreso = alumno.get(self._FIELD_ANIO_INGRESO)
                    id_ = alumno.get(self._FIELD_ID)  # Opcional

                    # Validaciones
                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError(self._MSG_INVALID_NAME)

                    if not isinstance(correo, str) or "@" not in correo:
                        raise ValueError(self._MSG_INVALID_EMAIL)

                    if not isinstance(anio_ingreso, int):
                        raise ValueError(self._MSG_INVALID_YEAR)

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError(self._MSG_INVALID_ID)

                    if id_:
                        # Intentar insertar con ID si viene
                        self.cursor.execute("""
                            INSERT INTO students (student_id, name, email, admission_date)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email)
                        """, (id_, nombre, correo, self._DATE_FORMAT.format(year=anio_ingreso)))
                    else:
                        # Insertar sin ID (autoincremental)
                        self.cursor.execute("""
                            INSERT INTO students (name, email, admission_date)
                            VALUES (%s, %s, %s)
                        """, (nombre, correo, self._DATE_FORMAT.format(year=anio_ingreso)))

                    insertados += 1

                except Exception as e:
                    errores.append(f"Alumno #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = f"{insertados} alumnos cargados. {len(errores)} errores.\n" + "\n".join(errores)
                return False, mensaje

            return True, f"{insertados} alumnos cargados exitosamente."

        except json.JSONDecodeError:
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar alumnos:", e)
            return False, self._MSG_PROCESSING_ERROR
    
    def load_profesores(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if self._KEY_PROFESORES not in raw_data or not isinstance(raw_data[self._KEY_PROFESORES], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_PROFESORES)

            profesores = raw_data[self._KEY_PROFESORES]
            
            # Validar tamaño máximo
            if len(profesores) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(profesores)} profesores. Máximo permitido: {self._MAX_ITEMS}."
            
            errores = []
            insertados = 0

            for i, prof in enumerate(profesores, start=1):
                try:
                    nombre = prof.get(self._FIELD_NOMBRE)
                    correo = prof.get(self._FIELD_CORREO)
                    id_ = prof.get(self._FIELD_ID)

                    # Validaciones
                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError(self._MSG_INVALID_NAME)

                    if not isinstance(correo, str) or not self.is_valid_email(correo):
                        raise ValueError(self._MSG_INVALID_EMAIL)

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError(self._MSG_INVALID_ID)

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
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar profesores:", e)
            return False, self._MSG_PROCESSING_ERROR

    def load_cursos(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if self._KEY_CURSOS not in raw_data or not isinstance(raw_data[self._KEY_CURSOS], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_CURSOS)

            cursos = raw_data[self._KEY_CURSOS]
            
            # Validar tamaño máximo
            if len(cursos) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(cursos)} cursos. Máximo permitido: {self._MAX_ITEMS}."
            
            errores = []
            insertados = 0

            for i, curso in enumerate(cursos, start=1):
                try:
                    id_ = curso.get(self._FIELD_ID)
                    name = curso.get(self._FIELD_DESCRIPCION)
                    codigo = curso.get(self._FIELD_CODIGO)
                    creditos = curso.get(self._FIELD_CREDITOS, 0)
                    requisitos = curso.get(self._FIELD_PRERREQUISITOS, [])

                    if not isinstance(name, str) or not name.strip():
                        raise ValueError("Descripción inválida (campo 'name')")

                    if not isinstance(codigo, str) or not codigo.strip():
                        raise ValueError(self._MSG_INVALID_CODE)

                    if not isinstance(creditos, int):
                        raise ValueError(self._MSG_INVALID_CREDITS)

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError("ID inválido (debe ser entero o nulo)")

                    if not isinstance(requisitos, list):
                        raise ValueError(self._MSG_INVALID_PREREQ)

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
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar cursos:", e)
            return False, self._MSG_INTERNAL_ERROR

    def load_instancias(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            anio = raw_data.get(self._FIELD_ANO)
            semestre = raw_data.get(self._FIELD_SEMESTRE)
            instancias = raw_data.get(self._KEY_INSTANCIAS, [])

            if not isinstance(anio, int):
                return False, "El campo 'año' debe ser un entero."

            if not isinstance(semestre, int) or semestre not in [self._MIN_SEMESTER, self._MAX_SEMESTER]:
                return False, f"El campo 'semestre' debe ser {self._MIN_SEMESTER} o {self._MAX_SEMESTER}."

            if not isinstance(instancias, list):
                return False, "El campo 'instancias' debe ser una lista."

            # Validar tamaño máximo
            if len(instancias) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(instancias)} instancias. Máximo permitido: {self._MAX_ITEMS}."

            errores = []
            insertados = 0
            for i, instancia in enumerate(instancias, start=1):
                try:
                    id_ = instancia.get(self._FIELD_ID)
                    curso_id = instancia.get(self._FIELD_CURSO_ID)

                    if not isinstance(curso_id, int):
                        raise ValueError("El campo 'curso_id' debe ser un entero.")

                    self.cursor.execute("SELECT 1 FROM courses WHERE course_id = %s", (curso_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(self._MSG_COURSE_NOT_EXISTS.format(id=curso_id))

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
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar instancias:", e)
            return False, self._MSG_INTERNAL_ERROR

    def load_enrollments(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if self._KEY_ALUMNOS_SECCION not in raw_data or not isinstance(raw_data[self._KEY_ALUMNOS_SECCION], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_ALUMNOS_SECCION)

            inscripciones = raw_data[self._KEY_ALUMNOS_SECCION]
            
            # Validar tamaño máximo
            if len(inscripciones) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(inscripciones)} inscripciones. Máximo permitido: {self._MAX_ITEMS}."
            
            errores = []
            insertados = 0

            for i, inscripcion in enumerate(inscripciones, start=1):
                try:
                    seccion_id = inscripcion.get(self._FIELD_SECCION_ID)
                    alumno_id = inscripcion.get(self._FIELD_ALUMNO_ID)

                    if not isinstance(seccion_id, int) or not isinstance(alumno_id, int):
                        raise ValueError("IDs inválidos (deben ser enteros)")

                    # Verificar existencia de section
                    self.cursor.execute("SELECT 1 FROM sections WHERE section_id = %s", (seccion_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(self._MSG_SECTION_NOT_EXISTS.format(id=seccion_id))

                    # Verificar existencia de student
                    self.cursor.execute("SELECT 1 FROM students WHERE student_id = %s", (alumno_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(self._MSG_STUDENT_NOT_EXISTS.format(id=alumno_id))

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
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar inscripciones:", e)
            return False, self._MSG_INTERNAL_ERROR

    def load_classrooms(self, file_storage):
        try:
            raw_data = json.load(file_storage)

            if self._KEY_SALAS not in raw_data or not isinstance(raw_data[self._KEY_SALAS], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_SALAS)

            salas = raw_data[self._KEY_SALAS]
            
            # Validar tamaño máximo
            if len(salas) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(salas)} salas. Máximo permitido: {self._MAX_ITEMS}."
            
            errores = []
            insertados = 0

            for i, sala in enumerate(salas, start=1):
                try:
                    id_ = sala.get(self._FIELD_ID)
                    nombre = sala.get(self._FIELD_NOMBRE)
                    capacidad = sala.get(self._FIELD_CAPACIDAD)

                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError(self._MSG_INVALID_NAME)

                    if not isinstance(capacidad, int) or capacidad <= 0:
                        raise ValueError(self._MSG_INVALID_CAPACITY)

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
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar salas:", e)
            return False, self._MSG_INTERNAL_ERROR

    def load_instancias_con_secciones(self, file_storage):
        try:
            data = json.load(file_storage)

            if self._KEY_SECCIONES not in data or not isinstance(data[self._KEY_SECCIONES], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_SECCIONES)

            secciones = data[self._KEY_SECCIONES]
            
            # Validar tamaño máximo
            if len(secciones) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(secciones)} secciones. Máximo permitido: {self._MAX_ITEMS}."
            
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
                    instance_id = int(seccion.get(self._FIELD_INSTANCIA_CURSO))
                    numero = int(seccion.get(self._FIELD_ID))
                    profesor_id = int(seccion.get(self._FIELD_PROFESOR_ID))

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

                    evaluacion = seccion.get(self._KEY_EVALUACION)
                    if evaluacion:
                        tipo_eval = evaluacion.get(self._FIELD_TIPO)
                        if tipo_eval not in (self._EVAL_TYPE_PESO, self._EVAL_TYPE_PORCENTAJE):
                            raise ValueError(f"Tipo de evaluación inválido: {tipo_eval}")

                        combinacion = evaluacion.get(self._KEY_COMBINACION_TOPICOS, [])
                        topicos = evaluacion.get(self._KEY_TOPICOS, {})

                        valores_topico = [float(t[self._FIELD_VALOR]) for t in combinacion]
                        if tipo_eval == self._EVAL_TYPE_PESO:
                            total = sum(valores_topico)
                            pesos_relativos = round_with_correction([v / total for v in valores_topico])
                        else:
                            pesos_relativos = round_with_correction([v / 100 for v in valores_topico])

                        for idx, topico_meta in enumerate(combinacion):
                            topico_id = str(topico_meta.get(self._FIELD_ID))
                            nombre = topico_meta.get(self._FIELD_NOMBRE)
                            peso_normalizado = pesos_relativos[idx]

                            if topico_id not in topicos:
                                raise ValueError(f"No hay descripción para el tópico con id {topico_id}")

                            self.cursor.execute("""
                                INSERT INTO evaluations (section_id, type, weight, optional)
                                VALUES (%s, %s, %s, %s)
                            """, (section_id, nombre, peso_normalizado, False))
                            evaluation_id = self.cursor.lastrowid

                            topico = topicos[topico_id]
                            cantidad = topico.get(self._FIELD_CANTIDAD)
                            valores = topico.get(self._FIELD_VALORES, [])
                            obligatorias = topico.get(self._FIELD_OBLIGATORIAS, [])

                            if cantidad != len(valores) or cantidad != len(obligatorias):
                                raise ValueError(f"Tópico {topico_id} tiene cantidades inconsistentes.")

                            if topico[self._FIELD_TIPO] == self._EVAL_TYPE_PESO:
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
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error en carga de secciones:", e)
            return False, self._MSG_INTERNAL_ERROR

    def load_notas(self, file_storage):
        try:
            data = json.load(file_storage)

            if self._KEY_NOTAS not in data or not isinstance(data[self._KEY_NOTAS], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_NOTAS)

            notas = data[self._KEY_NOTAS]
            
            # Validar tamaño máximo
            if len(notas) > self._MAX_ITEMS:
                return False, f"El archivo contiene {len(notas)} notas. Máximo permitido: {self._MAX_ITEMS}."
            
            insertadas = 0
            errores = []

            for i, nota_data in enumerate(notas, start=1):
                try:
                    required_fields = [self._FIELD_ALUMNO_ID, self._FIELD_TOPICO_ID, self._FIELD_INSTANCIA, self._FIELD_NOTA]
                    for field in required_fields:
                        if nota_data.get(field) is None:
                            raise ValueError(f"Campo '{field}' faltante o nulo")

                    alumno_id = int(nota_data[self._FIELD_ALUMNO_ID])
                    topico_id = int(nota_data[self._FIELD_TOPICO_ID])
                    instancia = int(nota_data[self._FIELD_INSTANCIA])
                    nota = float(nota_data[self._FIELD_NOTA])

                    if not (self._MIN_GRADE <= nota <= self._MAX_GRADE):
                        raise ValueError(self._MSG_GRADE_RANGE)

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
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            return False, self._MSG_INTERNAL_ERROR