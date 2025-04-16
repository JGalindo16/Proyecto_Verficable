import mysql.connector
import os
import random
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict

# Añadir la ruta raíz al path para poder importar la configuración desde cualquier ubicación
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """Crear conexión a la base de datos desde variables de entorno"""
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT')),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

def clear_existing_data(cursor):
    """Eliminar datos existentes en las tablas"""
    print("Eliminando datos existentes...")
    
    tables = [
        "grades", 
        "evaluation_instances", 
        "evaluations", 
        "enrollments", 
        "sections", 
        "course_instances", 
        "students", 
        "professors", 
        "courses"
    ]
    
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    
    print("Datos eliminados correctamente")

def insert_courses(cursor):
    """Insertar cursos de ejemplo"""
    print("Insertando cursos...")
    
    courses = [
        ("Diseño de Software Verificable", "IIC3745"),
        ("Programación Avanzada", "IIC2233"),
        ("Algoritmos y Estructuras de Datos", "IIC2133"),
        ("Ingeniería de Software", "IIC2143"),
        ("Base de Datos", "IIC2413"),
        ("Sistemas Operativos", "IIC2333"),
        ("Matemáticas Discretas", "IIC1253"),
        ("Cálculo I", "MAT1610"),
        ("Cálculo II", "MAT1620"),
        ("Álgebra Lineal", "MAT1203"),
        ("Estadística", "IIC2433"),
        ("Inteligencia Artificial", "IIC2613"),
        ("Arquitectura de Computadores", "IIC2343"),
        ("Computación Gráfica", "IIC2523"),
        ("Desarrollo Web", "IIC2513"),
        ("Aprendizaje de Máquina", "IIC2633"),
        ("Métodos de Optimización", "IIC3253"),
        ("Redes de Computadores", "IIC2523"),
        ("Lenguajes de Programación", "IIC2343"),
        ("Teoría de la Computación", "IIC2223")
    ]
    
    for name, code in courses:
        cursor.execute("INSERT INTO courses (name, code) VALUES (%s, %s)", (name, code))
    
    print(f"Se insertaron {len(courses)} cursos")

def insert_professors(cursor):
    """Insertar profesores de ejemplo"""
    print("Insertando profesores...")
    
    professors = [
        ("Carlos Rodríguez", "carlos.rodriguez@uc.cl"),
        ("María González", "maria.gonzalez@uc.cl"),
        ("Juan Pérez", "juan.perez@uc.cl"),
        ("Ana Martínez", "ana.martinez@uc.cl"),
        ("Roberto Silva", "roberto.silva@uc.cl"),
        ("Claudia Vásquez", "claudia.vasquez@uc.cl"),
        ("Pablo Muñoz", "pablo.munoz@uc.cl"),
        ("Daniela Castro", "daniela.castro@uc.cl"),
        ("Gabriel Torres", "gabriel.torres@uc.cl"),
        ("Valentina López", "valentina.lopez@uc.cl"),
        ("Hernán Soto", "hernan.soto@uc.cl"),
        ("Marcela Rojas", "marcela.rojas@uc.cl"),
        ("Alejandro Fuentes", "alejandro.fuentes@uc.cl"),
        ("Patricia Navarro", "patricia.navarro@uc.cl"),
        ("Ricardo Espinoza", "ricardo.espinoza@uc.cl"),
        # Profesores adicionales
        ("Ignacio Valenzuela", "ignacio.valenzuela@uc.cl"),
        ("Carmen Gutiérrez", "carmen.gutierrez@uc.cl"),
        ("Felipe Bravo", "felipe.bravo@uc.cl"),
        ("Laura Moreno", "laura.moreno@uc.cl"),
        ("Jorge Contreras", "jorge.contreras@uc.cl"),
        ("Pilar Vega", "pilar.vega@uc.cl"),
        ("Luis Tapia", "luis.tapia@uc.cl"),
        ("Isabel Campos", "isabel.campos@uc.cl"),
        ("Diego Reyes", "diego.reyes@uc.cl"),
        ("Francisca Muñoz", "francisca.munoz@uc.cl")
    ]
    
    for name, email in professors:
        cursor.execute("INSERT INTO professors (name, email) VALUES (%s, %s)", (name, email))
    
    print(f"Se insertaron {len(professors)} profesores")

def insert_students(cursor):
    """Insertar estudiantes de ejemplo"""
    print("Insertando estudiantes...")
    
    # Generar fechas de admisión aleatorias entre 2018 y 2023
    def random_admission_date():
        start_date = datetime(2018, 1, 1)
        end_date = datetime(2023, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date.strftime("%Y-%m-%d")
    
    # Apellidos comunes
    surnames = ["González", "Rodríguez", "Fernández", "López", "Martínez", 
                "Pérez", "Gómez", "Sánchez", "Díaz", "Torres", "Ramírez", 
                "Flores", "Vargas", "Rojas", "Morales", "Ortega", "Silva", 
                "Núñez", "Castro", "Campos", "Rivas", "Contreras", "Vega",
                "Gutiérrez", "Fuentes", "Hernández", "Reyes", "Valdés", "Vidal",
                "Muñoz", "Espinoza", "Cordero", "Araya", "Sepúlveda", "Aguilera",
                "Cárdenas", "Bravo", "Parra", "Tapia", "Carrasco", "Alarcón"]
    
    # Nombres comunes
    first_names = ["Matías", "Sofía", "Sebastián", "Valentina", "Felipe", 
                  "Camila", "Benjamín", "Isidora", "Nicolás", "Javiera", 
                  "Diego", "Antonia", "Vicente", "Francisca", "Gabriel", 
                  "Catalina", "Tomás", "Constanza", "Lucas", "Amanda",
                  "Ignacio", "Florencia", "Martín", "Esperanza", "Alejandro",
                  "Maite", "Joaquín", "Renata", "Maximiliano", "Agustina",
                  "Emilia", "Pablo", "Trinidad", "Cristóbal", "Daniela",
                  "Santiago", "Josefa", "Renato", "Fernanda", "Gaspar",
                  "Rocío", "Javier", "Magdalena", "Eduardo", "Victoria",
                  "Álvaro", "Consuelo", "Rodrigo", "Paulina", "Alonso"]
    
    # Generar 120 estudiantes (más de lo necesario para asegurar suficiente disponibilidad)
    students = []
    emails_used = set()
    
    for _ in range(120):
        first_name = random.choice(first_names)
        surname = random.choice(surnames)
        full_name = f"{first_name} {surname}"
        
        # Crear email único
        email_base = f"{first_name.lower()}.{surname.lower()}"
        email = f"{email_base}@uc.cl"
        counter = 1
        
        while email in emails_used:
            email = f"{email_base}{counter}@uc.cl"
            counter += 1
        
        emails_used.add(email)
        admission_date = random_admission_date()
        
        students.append((full_name, email, admission_date))
    
    for name, email, admission_date in students:
        cursor.execute("INSERT INTO students (name, email, admission_date) VALUES (%s, %s, %s)", 
                      (name, email, admission_date))
    
    print(f"Se insertaron {len(students)} estudiantes")

def insert_course_instances(cursor):
    """Insertar instancias de cursos para varios semestres"""
    print("Insertando instancias de cursos...")
    
    # Obtener IDs de cursos
    cursor.execute("SELECT course_id FROM courses")
    course_ids = [row[0] for row in cursor.fetchall()]
    
    # Crear instancias para los años 2021, 2022, 2023 y 2024, semestres 1 y 2
    years = [2021, 2022, 2023, 2024]
    semesters = ["1", "2"]
    
    instances = []
    for course_id in course_ids:
        for year in years:
            for semester in semesters:
                instances.append((course_id, year, semester))
    
    for course_id, year, semester in instances:
        cursor.execute("INSERT INTO course_instances (course_id, year, semester) VALUES (%s, %s, %s)", 
                      (course_id, year, semester))
    
    print(f"Se insertaron {len(instances)} instancias de cursos")

def insert_sections_and_enrollments(cursor):
    """Insertar secciones para cada instancia de curso y gestionar inscripciones de estudiantes"""
    print("Insertando secciones e inscripciones...")
    
    # Obtener IDs de instancias
    cursor.execute("SELECT instance_id, course_id FROM course_instances")
    instance_data = cursor.fetchall()
    
    # Organizar instancias por curso para garantizar que un estudiante no esté en más de una sección por curso
    course_instances = defaultdict(list)
    for instance in instance_data:
        course_instances[instance[1]].append(instance[0])
    
    # Obtener IDs de profesores
    cursor.execute("SELECT professor_id FROM professors")
    professor_ids = [row[0] for row in cursor.fetchall()]
    
    # Obtener todos los estudiantes
    cursor.execute("SELECT student_id FROM students")
    all_student_ids = [row[0] for row in cursor.fetchall()]
    
    # Diccionario para rastrear las asignaciones de estudiantes por instancia de curso
    # Estructura: {instance_id: {student_id: section_id}}
    student_assignments = defaultdict(dict)
    
    # Mapeo de cursos a estudiantes asignados (para reutilización entre instancias)
    # Estructura: {course_id: [lista de student_ids]}
    course_student_pool = {}
    
    sections_created = 0
    enrollments_created = 0
    
    # Para cada curso, creamos secciones y asignamos estudiantes
    for course_id, instances in course_instances.items():
        # Crear un pool de 30-60 estudiantes para este curso (que se reutilizará en diferentes instancias)
        if course_id not in course_student_pool:
            num_course_students = random.randint(30, min(60, len(all_student_ids)))
            course_student_pool[course_id] = random.sample(all_student_ids, num_course_students)
        
        course_students = course_student_pool[course_id]
        
        for instance_id in instances:
            # Crear entre 1 y 3 secciones para esta instancia
            num_sections = random.randint(1, 3)
            sections = []
            
            # Dividir el pool de estudiantes entre las secciones
            students_per_section = []
            remaining_students = course_students.copy()
            
            for i in range(num_sections):
                # Para la última sección, usar todos los estudiantes restantes
                if i == num_sections - 1:
                    students_per_section.append(remaining_students)
                else:
                    # Calcular cuántos estudiantes asignar a esta sección
                    section_size = len(remaining_students) // (num_sections - i)
                    section_students = random.sample(remaining_students, section_size)
                    students_per_section.append(section_students)
                    
                    # Eliminar los estudiantes asignados del grupo restante
                    for student_id in section_students:
                        remaining_students.remove(student_id)
            
            # Crear secciones y asignar estudiantes
            for section_num in range(1, num_sections + 1):
                # Asignar un profesor aleatorio
                professor_id = random.choice(professor_ids)
                
                # Insertar la sección
                cursor.execute(
                    "INSERT INTO sections (instance_id, number, professor_id) VALUES (%s, %s, %s)", 
                    (instance_id, section_num, professor_id)
                )
                section_id = cursor.lastrowid
                sections_created += 1
                
                # Asignar estudiantes a la sección
                section_students = students_per_section[section_num - 1]
                for student_id in section_students:
                    cursor.execute(
                        "INSERT INTO enrollments (student_id, section_id) VALUES (%s, %s)", 
                        (student_id, section_id)
                    )
                    enrollments_created += 1
                    
                    # Registrar esta asignación
                    student_assignments[instance_id][student_id] = section_id
                
                # Guardar la sección y su información para el retorno
                sections.append({
                    'id': section_id,
                    'number': section_num, 
                    'professor_id': professor_id, 
                    'students': section_students
                })
    
    print(f"Se insertaron {sections_created} secciones")
    print(f"Se insertaron {enrollments_created} inscripciones")
    
    return student_assignments

def insert_evaluations_and_grades(cursor, student_assignments):
    """Insertar evaluaciones y calificaciones para todos los estudiantes"""
    print("Insertando evaluaciones y calificaciones...")
    
    # Obtener todas las secciones por instancia
    cursor.execute("""
        SELECT s.section_id, s.instance_id, ci.course_id, ci.year, ci.semester
        FROM sections s
        JOIN course_instances ci ON s.instance_id = ci.instance_id
    """)
    sections_data = cursor.fetchall()
    
    # Agrupar secciones por instancia
    instances_sections = defaultdict(list)
    for section in sections_data:
        instances_sections[section[1]].append({
            'section_id': section[0],
            'instance_id': section[1],
            'course_id': section[2],
            'year': section[3],
            'semester': section[4]
        })
    
    total_evaluations = 0
    total_evaluation_instances = 0
    total_grades = 0
    
    # Para cada instancia de curso, crear evaluaciones consistentes entre todas sus secciones
    for instance_id, sections in instances_sections.items():
        # Definir los tipos de evaluación para esta instancia
        evaluation_types = []
        
        # Siempre añadimos un examen
        evaluation_types.append(("Examen", 0.4, False))
        
        # Elegir aleatoriamente entre otros tipos de evaluación
        possible_types = [
            ("Control", 0.3, False),
            ("Tarea", 0.2, False),
            ("Proyecto", 0.1, False),
            ("Presentación", 0.1, False)
        ]
        
        # Seleccionar 2-3 tipos adicionales de evaluación
        num_additional = random.randint(2, 3)
        selected_types = random.sample(possible_types, num_additional)
        evaluation_types.extend(selected_types)
        
        # Normalizar los pesos para que sumen 1.0
        total_weight = sum(t[1] for t in evaluation_types)
        evaluation_types = [(t[0], t[1]/total_weight, t[2]) for t in evaluation_types]
        
        # Definir cuántas instancias de cada tipo de evaluación habrá
        evaluation_instances_count = {}
        for eval_type, _, _ in evaluation_types:
            if eval_type == "Examen":
                # Solo 1 examen
                evaluation_instances_count[eval_type] = 1
            elif eval_type == "Control":
                # 2-4 controles
                evaluation_instances_count[eval_type] = random.randint(2, 4)
            elif eval_type == "Tarea":
                # 3-6 tareas
                evaluation_instances_count[eval_type] = random.randint(3, 6)
            elif eval_type == "Proyecto":
                # 1 proyecto
                evaluation_instances_count[eval_type] = 1
            else:
                # Otros tipos, 1-2 instancias
                evaluation_instances_count[eval_type] = random.randint(1, 2)
        
        # Para cada sección, insertar las evaluaciones
        evaluation_instances_by_type = {}
        for section in sections:
            section_id = section['section_id']
            
            # Insertar tipos de evaluación
            for eval_type, weight, optional in evaluation_types:
                cursor.execute(
                    "INSERT INTO evaluations (section_id, type, weight, optional) VALUES (%s, %s, %s, %s)",
                    (section_id, eval_type, weight, optional)
                )
                evaluation_id = cursor.lastrowid
                total_evaluations += 1
                
                # Crear instancias de evaluación
                instances_for_type = []
                instance_count = evaluation_instances_count[eval_type]
                
                for i in range(1, instance_count + 1):
                    name = f"{eval_type} {i}"
                    specific_weight = 1.0 / instance_count
                    mandatory = True if random.random() > 0.1 else False
                    
                    cursor.execute("""
                        INSERT INTO evaluation_instances 
                        (evaluation_id, name, specific_weight, mandatory) 
                        VALUES (%s, %s, %s, %s)
                    """, (evaluation_id, name, specific_weight, mandatory))
                    instance_eval_id = cursor.lastrowid
                    total_evaluation_instances += 1
                    instances_for_type.append(instance_eval_id)
                
                # Guardar las instancias de evaluación para este tipo
                if eval_type not in evaluation_instances_by_type:
                    evaluation_instances_by_type[eval_type] = {}
                evaluation_instances_by_type[eval_type][section_id] = instances_for_type
        
        # Ahora asignar notas a los estudiantes
        for student_id, section_id in student_assignments[instance_id].items():
            # Primero obtener el ID de inscripción
            cursor.execute(
                "SELECT enrollment_id FROM enrollments WHERE student_id = %s AND section_id = %s",
                (student_id, section_id)
            )
            enrollment = cursor.fetchone()
            if not enrollment:
                continue  # Saltamos si no hay inscripción (no debería ocurrir)
                
            enrollment_id = enrollment[0]
            
            # Asignar notas para todas las instancias de evaluación de esta sección
            for eval_type, sections_instances in evaluation_instances_by_type.items():
                if section_id not in sections_instances:
                    continue
                    
                for instance_eval_id in sections_instances[section_id]:
                    # Generar una nota aleatoria con distribución realista
                    if random.random() < 0.7:  # 70% notas aprobatorias
                        score = round(random.uniform(4.0, 7.0), 1)
                    else:
                        score = round(random.uniform(1.0, 3.9), 1)
                        
                    # Insertar la nota
                    cursor.execute(
                        "INSERT INTO grades (instance_eval_id, enrollment_id, score) VALUES (%s, %s, %s)",
                        (instance_eval_id, enrollment_id, score)
                    )
                    total_grades += 1

    print(f"Se insertaron {total_evaluations} evaluaciones")
    print(f"Se insertaron {total_evaluation_instances} instancias de evaluación")
    print(f"Se insertaron {total_grades} calificaciones")

def main():
    """Función principal para poblar la base de datos"""
    print("Iniciando la población de la base de datos...")
    
    # Obtener conexión y cursor
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Desactivar verificación de claves foráneas temporalmente para limpiar datos
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Poblar la base de datos
        clear_existing_data(cursor)
        insert_courses(cursor)
        insert_professors(cursor)
        insert_students(cursor)
        insert_course_instances(cursor)
        
        # Insertar secciones y estudiantes (con las restricciones de asignación)
        student_assignments = insert_sections_and_enrollments(cursor)
        
        # Insertar evaluaciones y calificaciones para todas las asignaciones
        insert_evaluations_and_grades(cursor, student_assignments)
        
        # Reactivar verificación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Confirmar todos los cambios
        connection.commit()
        
        print("\n¡Base de datos poblada exitosamente!")
        print(f"Recuerda revisar la aplicación en http://localhost:5000")
        
    except Exception as e:
        # En caso de error, revertir cambios
        connection.rollback()
        print(f"Error al poblar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cerrar conexiones
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
