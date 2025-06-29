import json
import re
from datetime import date
from app.db import DatabaseConnection
from app.sql_queries.json_queries import *

class JsonUploadService:
    
    _MAX_ITEMS = 100
    _EMAIL_PATTERN = r"[^@]+@[^@]+\.[^@]+"

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
    
    _EVAL_TYPE_PESO = "peso"
    _EVAL_TYPE_PORCENTAJE = "porcentaje"
    
    _MIN_GRADE = 1.0
    _MAX_GRADE = 7.0
    _MIN_SEMESTER = 1
    _MAX_SEMESTER = 2
    
    _MSG_NO_JSON_KEY = ("El JSON debe contener una lista bajo la clave "
                        "'{key}'.")
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
    _MSG_INVALID_CAPACITY = ("Capacidad inválida (debe ser un número "
                            "entero positivo)")
    _MSG_COURSE_NOT_EXISTS = "El curso_id {id} no existe."
    _MSG_STUDENT_NOT_EXISTS = "El alumno con ID {id} no existe"
    _MSG_SECTION_NOT_EXISTS = "La sección con ID {id} no existe"
    _MSG_GRADE_RANGE = (f"La nota debe estar entre {_MIN_GRADE} y "
                       f"{_MAX_GRADE}.")
    
    _DATE_FORMAT = "{year}-01-01"
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.connect()

    def is_valid_email(self, email):
        """Check if email format is valid."""
        return re.match(self._EMAIL_PATTERN, email)

    def email_exists(self, email):
        """Check if email already exists in database."""
        self.cursor.execute(CHECK_EMAIL_EXISTS, (email,))
        return self.cursor.fetchone() is not None

    def _validate_course_data(self, curso, i):
        """Validate individual course data."""
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

        return id_, name, codigo, creditos, requisitos

    def _insert_course(self, id_, codigo, name, creditos):
        """Insert course into database."""
        if id_:
            self.cursor.execute(
                INSERT_COURSE_WITH_ID, (id_, codigo, name, creditos)
            )
            return id_
        else:
            self.cursor.execute(INSERT_COURSE, (codigo, name, creditos))
            return self.cursor.lastrowid

    def _process_course_prerequisites(self, course_id, requisitos):
        """Process and insert course prerequisites."""
        for code in requisitos:
            if not isinstance(code, str) or not code.strip():
                raise ValueError("Código de prerrequisito inválido")

            self.cursor.execute(SELECT_PREREQUISITE_ID_BY_CODE, (code,))
            result = self.cursor.fetchone()
            if not result:
                raise ValueError(
                    f"El prerrequisito '{code}' no existe en la base de datos"
                )

            prereq_id = result['course_id']
            self.cursor.execute(
                INSERT_COURSE_PREREQUISITE, (course_id, prereq_id)
            )
    
    def load_alumnos(self, file_storage):
        """Load students from JSON file."""
        try:
            raw_data = json.load(file_storage)

            if (self._KEY_ALUMNOS not in raw_data or 
                not isinstance(raw_data[self._KEY_ALUMNOS], list)):
                return False, self._MSG_NO_JSON_KEY.format(
                    key=self._KEY_ALUMNOS
                )

            alumnos = raw_data[self._KEY_ALUMNOS]
            
            if len(alumnos) > self._MAX_ITEMS:
                return False, (f"El archivo contiene {len(alumnos)} alumnos. "
                              f"Máximo permitido: {self._MAX_ITEMS}.")
            
            errores = []
            insertados = 0

            for i, alumno in enumerate(alumnos, start=1):
                try:
                    nombre = alumno.get(self._FIELD_NOMBRE)
                    correo = alumno.get(self._FIELD_CORREO)
                    anio_ingreso = alumno.get(self._FIELD_ANIO_INGRESO)
                    id_ = alumno.get(self._FIELD_ID)

                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError(self._MSG_INVALID_NAME)

                    if not isinstance(correo, str) or "@" not in correo:
                        raise ValueError(self._MSG_INVALID_EMAIL)

                    if not isinstance(anio_ingreso, int):
                        raise ValueError(self._MSG_INVALID_YEAR)

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError(self._MSG_INVALID_ID)

                    if id_:
                        self.cursor.execute(
                            INSERT_STUDENT_WITH_ID, 
                            (id_, nombre, correo, 
                             self._DATE_FORMAT.format(year=anio_ingreso))
                        )
                    else:
                        self.cursor.execute(
                            INSERT_STUDENT, 
                            (nombre, correo, 
                             self._DATE_FORMAT.format(year=anio_ingreso))
                        )

                    insertados += 1

                except Exception as e:
                    errores.append(f"Alumno #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = (f"{insertados} alumnos cargados. "
                          f"{len(errores)} errores.\n" + "\n".join(errores))
                return False, mensaje

            return True, f"{insertados} alumnos cargados exitosamente."

        except json.JSONDecodeError:
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar alumnos:", e)
            return False, self._MSG_PROCESSING_ERROR
    
    def load_profesores(self, file_storage):
        """Load professors from JSON file."""
        try:
            raw_data = json.load(file_storage)

            if (self._KEY_PROFESORES not in raw_data or 
                not isinstance(raw_data[self._KEY_PROFESORES], list)):
                return False, self._MSG_NO_JSON_KEY.format(
                    key=self._KEY_PROFESORES
                )

            profesores = raw_data[self._KEY_PROFESORES]
            
            if len(profesores) > self._MAX_ITEMS:
                return False, (f"El archivo contiene {len(profesores)} "
                              f"profesores. Máximo permitido: "
                              f"{self._MAX_ITEMS}.")
            
            errores = []
            insertados = 0

            for i, prof in enumerate(profesores, start=1):
                try:
                    nombre = prof.get(self._FIELD_NOMBRE)
                    correo = prof.get(self._FIELD_CORREO)
                    id_ = prof.get(self._FIELD_ID)

                    if not isinstance(nombre, str) or not nombre.strip():
                        raise ValueError(self._MSG_INVALID_NAME)

                    if (not isinstance(correo, str) or 
                        not self.is_valid_email(correo)):
                        raise ValueError(self._MSG_INVALID_EMAIL)

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError(self._MSG_INVALID_ID)

                    if id_:
                        self.cursor.execute(
                            INSERT_PROFESSOR_WITH_ID, (id_, nombre, correo)
                        )
                    else:
                        self.cursor.execute(
                            INSERT_PROFESSOR, (nombre, correo)
                        )

                    insertados += 1

                except Exception as e:
                    errores.append(f"Profesor #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = (f"{insertados} profesores cargados. "
                          f"{len(errores)} errores.\n" + "\n".join(errores))
                return False, mensaje

            return True, f"{insertados} profesores cargados exitosamente."

        except json.JSONDecodeError:
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar profesores:", e)
            return False, self._MSG_PROCESSING_ERROR

    def load_cursos(self, file_storage):
        """Load courses from JSON file."""
        try:
            raw_data = json.load(file_storage)

            if (self._KEY_CURSOS not in raw_data or 
                not isinstance(raw_data[self._KEY_CURSOS], list)):
                return False, self._MSG_NO_JSON_KEY.format(
                    key=self._KEY_CURSOS
                )

            cursos = raw_data[self._KEY_CURSOS]
            
            if len(cursos) > self._MAX_ITEMS:
                return False, (f"El archivo contiene {len(cursos)} cursos. "
                              f"Máximo permitido: {self._MAX_ITEMS}.")
            
            errores = []
            insertados = 0

            for i, curso in enumerate(cursos, start=1):
                try:
                    # Validate course data
                    id_, name, codigo, creditos, requisitos = (
                        self._validate_course_data(curso, i)
                    )

                    # Insert course
                    course_id = self._insert_course(id_, codigo, name, creditos)

                    # Process prerequisites
                    self._process_course_prerequisites(course_id, requisitos)

                    insertados += 1

                except Exception as e:
                    errores.append(f"Curso #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = (f"{insertados} cursos cargados. "
                          f"{len(errores)} errores.\n" + "\n".join(errores))
                return False, mensaje

            return True, f"{insertados} cursos cargados exitosamente."

        except json.JSONDecodeError:
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar cursos:", e)
            return False, self._MSG_INTERNAL_ERROR

    def load_instancias(self, file_storage):
        """Load course instances from JSON file."""
        try:
            raw_data = json.load(file_storage)

            anio = raw_data.get(self._FIELD_ANO)
            semestre = raw_data.get(self._FIELD_SEMESTRE)
            instancias = raw_data.get(self._KEY_INSTANCIAS, [])

            if not isinstance(anio, int):
                return False, "El campo 'año' debe ser un entero."

            if (not isinstance(semestre, int) or 
                semestre not in [self._MIN_SEMESTER, self._MAX_SEMESTER]):
                return False, (f"El campo 'semestre' debe ser "
                              f"{self._MIN_SEMESTER} o {self._MAX_SEMESTER}.")

            if not isinstance(instancias, list):
                return False, "El campo 'instancias' debe ser una lista."

            if len(instancias) > self._MAX_ITEMS:
                return False, (f"El archivo contiene {len(instancias)} "
                              f"instancias. Máximo permitido: "
                              f"{self._MAX_ITEMS}.")

            errores = []
            insertados = 0
            for i, instancia in enumerate(instancias, start=1):
                try:
                    id_ = instancia.get(self._FIELD_ID)
                    curso_id = instancia.get(self._FIELD_CURSO_ID)

                    if not isinstance(curso_id, int):
                        raise ValueError(
                            "El campo 'curso_id' debe ser un entero."
                        )

                    self.cursor.execute(CHECK_COURSE_EXISTS, (curso_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(
                            self._MSG_COURSE_NOT_EXISTS.format(id=curso_id)
                        )

                    if id_ is not None and not isinstance(id_, int):
                        raise ValueError(
                            "El campo 'id' debe ser entero o no estar presente."
                        )

                    if id_:
                        self.cursor.execute(
                            INSERT_INSTANCE_WITH_ID, 
                            (id_, curso_id, anio, str(semestre))
                        )
                    else:
                        self.cursor.execute(
                            INSERT_INSTANCE, (curso_id, anio, str(semestre))
                        )

                    insertados += 1
                except Exception as e:
                    errores.append(f"Instancia #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = (f"{insertados} instancias cargadas. "
                          f"{len(errores)} errores.\n" + "\n".join(errores))
                return False, mensaje

            return True, f"{insertados} instancias cargadas exitosamente."

        except json.JSONDecodeError:
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error al cargar instancias:", e)
            return False, self._MSG_INTERNAL_ERROR

    def _round_with_correction(self, values):
        """Helper function to round values with correction."""
        rounded = [round(v, 2) for v in values]
        diff = round(1.0 - sum(rounded), 2)
        if rounded:
            rounded[-1] += diff
        return rounded

    def _validate_section_basic_data(self, seccion):
        """Validate basic section data."""
        instance_id = int(seccion.get(self._FIELD_INSTANCIA_CURSO))
        numero = int(seccion.get(self._FIELD_ID))
        profesor_id = int(seccion.get(self._FIELD_PROFESOR_ID))

        self.cursor.execute(CHECK_INSTANCE_EXISTS, (instance_id,))
        if not self.cursor.fetchone():
            raise ValueError(f"Instancia con ID {instance_id} no existe")

        self.cursor.execute(CHECK_PROFESSOR_EXISTS, (profesor_id,))
        if not self.cursor.fetchone():
            raise ValueError(f"Profesor con ID {profesor_id} no existe")

        return instance_id, numero, profesor_id

    def _create_section(self, instance_id, numero, profesor_id):
        """Create section in database."""
        self.cursor.execute(INSERT_SECTION, (instance_id, numero, profesor_id))
        return self.cursor.lastrowid

    def _validate_evaluation_data(self, evaluacion):
        """Validate evaluation structure."""
        tipo_eval = evaluacion.get(self._FIELD_TIPO)
        if tipo_eval not in (self._EVAL_TYPE_PESO, self._EVAL_TYPE_PORCENTAJE):
            raise ValueError(f"Tipo de evaluación inválido: {tipo_eval}")

        combinacion = evaluacion.get(self._KEY_COMBINACION_TOPICOS, [])
        topicos = evaluacion.get(self._KEY_TOPICOS, {})

        return tipo_eval, combinacion, topicos

    def _calculate_topic_weights(self, combinacion, tipo_eval):
        """Calculate normalized weights for topics."""
        valores_topico = [float(t[self._FIELD_VALOR]) for t in combinacion]
        
        if tipo_eval == self._EVAL_TYPE_PESO:
            total = sum(valores_topico)
            pesos_relativos = self._round_with_correction(
                [v / total for v in valores_topico]
            )
        else:
            pesos_relativos = self._round_with_correction(
                [v / 100 for v in valores_topico]
            )
        
        return pesos_relativos

    def _validate_topic_consistency(self, topico_id, topico):
        """Validate topic data consistency."""
        cantidad = topico.get(self._FIELD_CANTIDAD)
        valores = topico.get(self._FIELD_VALORES, [])
        obligatorias = topico.get(self._FIELD_OBLIGATORIAS, [])

        if cantidad != len(valores) or cantidad != len(obligatorias):
            raise ValueError(
                f"Tópico {topico_id} tiene cantidades inconsistentes."
            )

        return cantidad, valores, obligatorias

    def _calculate_instance_weights(self, topico, valores):
        """Calculate normalized weights for evaluation instances."""
        if topico[self._FIELD_TIPO] == self._EVAL_TYPE_PESO:
            total = sum(valores)
            instancias_pesos = self._round_with_correction(
                [v / total for v in valores]
            )
        else:
            instancias_pesos = self._round_with_correction(
                [v / 100 for v in valores]
            )
        
        return instancias_pesos

    def _create_evaluation_instances(self, evaluation_id, nombre, cantidad, 
                                   instancias_pesos, obligatorias):
        """Create evaluation instances in database."""
        for j in range(cantidad):
            self.cursor.execute(
                INSERT_EVALUATION_INSTANCE, (
                    evaluation_id,
                    f"{nombre} Instancia {j + 1}",
                    instancias_pesos[j],
                    obligatorias[j]
                )
            )

    def _process_section_evaluation(self, section_id, evaluacion):
        """Process evaluation structure for a section."""
        tipo_eval, combinacion, topicos = self._validate_evaluation_data(
            evaluacion
        )
        pesos_relativos = self._calculate_topic_weights(combinacion, tipo_eval)

        for idx, topico_meta in enumerate(combinacion):
            topico_id = str(topico_meta.get(self._FIELD_ID))
            nombre = topico_meta.get(self._FIELD_NOMBRE)
            peso_normalizado = pesos_relativos[idx]

            if topico_id not in topicos:
                raise ValueError(
                    f"No hay descripción para el tópico con id {topico_id}"
                )

            self.cursor.execute(
                INSERT_EVALUATION, 
                (section_id, nombre, peso_normalizado, False)
            )
            evaluation_id = self.cursor.lastrowid

            topico = topicos[topico_id]
            cantidad, valores, obligatorias = self._validate_topic_consistency(
                topico_id, topico
            )
            
            instancias_pesos = self._calculate_instance_weights(topico, valores)
            
            self._create_evaluation_instances(
                evaluation_id, nombre, cantidad, instancias_pesos, obligatorias
            )

    def _process_section_with_evaluations(self, seccion):
        """Process a complete section including its evaluations."""
        instance_id, numero, profesor_id = (
            self._validate_section_basic_data(seccion)
        )

        section_id = self._create_section(instance_id, numero, profesor_id)

        evaluacion = seccion.get(self._KEY_EVALUACION)
        if evaluacion:
            self._process_section_evaluation(section_id, evaluacion)

        return section_id

    def load_enrollments(self, file_storage):
        """Load student enrollments from JSON file."""
        try:
            raw_data = json.load(file_storage)

            if self._KEY_ALUMNOS_SECCION not in raw_data or not isinstance(raw_data[self._KEY_ALUMNOS_SECCION], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_ALUMNOS_SECCION)

            inscripciones = raw_data[self._KEY_ALUMNOS_SECCION]
            
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

                    self.cursor.execute(CHECK_SECTION_EXISTS, (seccion_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(self._MSG_SECTION_NOT_EXISTS.format(id=seccion_id))

                    self.cursor.execute(CHECK_STUDENT_EXISTS, (alumno_id,))
                    if not self.cursor.fetchone():
                        raise ValueError(self._MSG_STUDENT_NOT_EXISTS.format(id=alumno_id))

                    self.cursor.execute(INSERT_ENROLLMENT, (alumno_id, seccion_id))

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
        """Load classrooms from JSON file."""
        try:
            raw_data = json.load(file_storage)

            if self._KEY_SALAS not in raw_data or not isinstance(raw_data[self._KEY_SALAS], list):
                return False, self._MSG_NO_JSON_KEY.format(key=self._KEY_SALAS)

            salas = raw_data[self._KEY_SALAS]
            
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
                        self.cursor.execute(INSERT_CLASSROOM_WITH_ID, (id_, nombre, capacidad))
                    else:
                        self.cursor.execute(INSERT_CLASSROOM, (nombre, capacidad))

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
        """Load instances with sections from JSON file."""
        try:
            data = json.load(file_storage)

            is_valid, result = self._validate_json_structure_for_sections(data)
            if not is_valid:
                return False, result
            
            secciones = result
            insertadas = 0
            errores = []

            for i, seccion in enumerate(secciones, start=1):
                try:
                    self._process_section_with_evaluations(seccion)
                    insertadas += 1

                except Exception as e:
                    errores.append(f"Sección #{i}: {str(e)}")

            self.db.commit()

            if errores:
                return False, (f"{insertadas} secciones cargadas con éxito. "
                              f"{len(errores)} errores.\n" + 
                              "\n".join(errores))
            return True, f"{insertadas} secciones cargadas exitosamente."

        except json.JSONDecodeError:
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            print("Error en carga de secciones:", e)
            return False, self._MSG_INTERNAL_ERROR

    def load_notas(self, file_storage):
        """Load grades from JSON file."""
        try:
            data = json.load(file_storage)

            if (self._KEY_NOTAS not in data or 
                not isinstance(data[self._KEY_NOTAS], list)):
                return False, self._MSG_NO_JSON_KEY.format(
                    key=self._KEY_NOTAS
                )

            notas = data[self._KEY_NOTAS]
            
            if len(notas) > self._MAX_ITEMS:
                return False, (f"El archivo contiene {len(notas)} notas. "
                              f"Máximo permitido: {self._MAX_ITEMS}.")
            
            insertadas = 0
            errores = []

            for i, nota_data in enumerate(notas, start=1):
                try:
                    required_fields = [
                        self._FIELD_ALUMNO_ID, self._FIELD_TOPICO_ID, 
                        self._FIELD_INSTANCIA, self._FIELD_NOTA
                    ]
                    for field in required_fields:
                        if nota_data.get(field) is None:
                            raise ValueError(
                                f"Campo '{field}' faltante o nulo"
                            )

                    alumno_id = int(nota_data[self._FIELD_ALUMNO_ID])
                    topico_id = int(nota_data[self._FIELD_TOPICO_ID])
                    instancia = int(nota_data[self._FIELD_INSTANCIA])
                    nota = float(nota_data[self._FIELD_NOTA])

                    if not (self._MIN_GRADE <= nota <= self._MAX_GRADE):
                        raise ValueError(self._MSG_GRADE_RANGE)

                    self.cursor.execute(
                        "SELECT 1 FROM students WHERE student_id = %s", 
                        (alumno_id,)
                    )
                    if not self.cursor.fetchone():
                        raise ValueError(
                            f"Alumno con ID {alumno_id} no existe"
                        )

                    self.cursor.execute(
                        SELECT_INSTANCE_EVAL_AND_SECTION, 
                        (topico_id, f"%Instancia {instancia}")
                    )
                    result = self.cursor.fetchone()
                    if not result:
                        raise ValueError(
                            f"No existe la instancia {instancia} para el "
                            f"tópico {topico_id}"
                        )

                    instance_eval_id = result["instance_eval_id"]
                    section_id = result["section_id"]

                    self.cursor.execute(
                        SELECT_ENROLLMENT_ID, (alumno_id, section_id)
                    )
                    result = self.cursor.fetchone()
                    if not result:
                        raise ValueError(
                            f"El alumno {alumno_id} no está inscrito en la "
                            f"sección {section_id}"
                        )
                    
                    enrollment_id = result["enrollment_id"]

                    self.cursor.execute(
                        INSERT_GRADE, (enrollment_id, instance_eval_id, nota)
                    )

                    insertadas += 1

                except Exception as e:
                    errores.append(f"Nota #{i}: {str(e)}")

            self.db.commit()

            if errores:
                mensaje = (f"{insertadas} notas cargadas con éxito. "
                          f"{len(errores)} errores.\n" + "\n".join(errores))
                return False, mensaje

            return True, f"{insertadas} notas cargadas exitosamente."

        except json.JSONDecodeError:
            return False, self._MSG_INVALID_JSON
        except Exception as e:
            return False, self._MSG_INTERNAL_ERROR

    def _validate_json_structure_for_sections(self, data):
        """Validate JSON structure for sections loading."""
        if (self._KEY_SECCIONES not in data or 
            not isinstance(data[self._KEY_SECCIONES], list)):
            return False, self._MSG_NO_JSON_KEY.format(
                key=self._KEY_SECCIONES
            )

        secciones = data[self._KEY_SECCIONES]
        
        if len(secciones) > self._MAX_ITEMS:
            return False, (f"El archivo contiene {len(secciones)} "
                          f"secciones. Máximo permitido: "
                          f"{self._MAX_ITEMS}.")
        
        return True, secciones