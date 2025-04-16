import mysql.connector
import os
import random
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

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
    
    # Generar 100 estudiantes (aumentado de 50)
    students = []
    emails_used = set()
    
    for _ in range(100):
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

def insert_sections(cursor):
    """Insertar secciones para cada instancia de curso"""
    print("Insertando secciones...")
    
    # Obtener IDs de instancias
    cursor.execute("SELECT instance_id FROM course_instances")
    instance_ids = [row[0] for row in cursor.fetchall()]
    
    # Obtener IDs de profesores
    cursor.execute("SELECT professor_id FROM professors")
    professor_ids = [row[0] for row in cursor.fetchall()]
    
    sections = []
    for instance_id in instance_ids:
        # Crear entre 1 y 5 secciones para cada instancia (aumentado de 4)
        num_sections = random.randint(1, 5)
        for section_num in range(1, num_sections + 1):
            # Asignar un profesor aleatorio
            professor_id = random.choice(professor_ids)
            sections.append((instance_id, section_num, professor_id))
    
    for instance_id, number, professor_id in sections:
        cursor.execute("INSERT INTO sections (instance_id, number, professor_id) VALUES (%s, %s, %s)", 
                      (instance_id, number, professor_id))
    
    print(f"Se insertaron {len(sections)} secciones")

def insert_enrollments(cursor):
    """Inscribir estudiantes en las secciones"""
    print("Inscribiendo estudiantes en secciones...")
    
    # Obtener IDs de secciones
    cursor.execute("SELECT section_id FROM sections")
    section_ids = [row[0] for row in cursor.fetchall()]
    
    # Obtener IDs de estudiantes
    cursor.execute("SELECT student_id FROM students")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    enrollments = []
    # Para cada sección, inscribir entre 10 y 30 estudiantes aleatorios (aumentado)
    for section_id in section_ids:
        # Determinar cuántos estudiantes se inscribirán en esta sección
        num_students = random.randint(10, min(30, len(student_ids)))
        
        # Seleccionar estudiantes aleatorios sin repetir
        selected_students = random.sample(student_ids, num_students)
        
        for student_id in selected_students:
            enrollments.append((student_id, section_id))
    
    for student_id, section_id in enrollments:
        cursor.execute("INSERT INTO enrollments (student_id, section_id) VALUES (%s, %s)", 
                      (student_id, section_id))
    
    print(f"Se insertaron {len(enrollments)} matrículas")

def insert_evaluations(cursor):
    """Insertar evaluaciones para las secciones"""
    print("Insertando evaluaciones...")
    
    # Obtener IDs de secciones
    cursor.execute("SELECT section_id FROM sections")
    section_ids = [row[0] for row in cursor.fetchall()]
    
    # Tipos comunes de evaluaciones con sus pesos
    evaluation_types = [
        ("Examen", 0.3, False),
        ("Control", 0.4, False),
        ("Tarea", 0.2, False),
        ("Proyecto", 0.1, False)  # Añadido un tipo más de evaluación
    ]
    
    evaluations = []
    for section_id in section_ids:
        for eval_type, weight, optional in evaluation_types:
            evaluations.append((section_id, eval_type, weight, optional))
    
    for section_id, eval_type, weight, optional in evaluations:
        cursor.execute("INSERT INTO evaluations (section_id, type, weight, optional) VALUES (%s, %s, %s, %s)", 
                      (section_id, eval_type, weight, optional))
    
    print(f"Se insertaron {len(evaluations)} evaluaciones")
    
    # Ahora insertamos las instancias de evaluación
    cursor.execute("SELECT evaluation_id, type FROM evaluations")
    evaluation_data = cursor.fetchall()
    
    evaluation_instances = []
    for eval_data in evaluation_data:
        eval_id = eval_data[0]
        eval_type = eval_data[1]
        
        # Determinar cuántas instancias de esta evaluación habrá
        if eval_type == "Examen":
            num_instances = random.randint(1, 2)  # Posibilidad de examen de recuperación
        elif eval_type == "Control":
            num_instances = random.randint(3, 5)  # Más controles
        elif eval_type == "Proyecto":
            num_instances = 1
        else:  # Tareas
            num_instances = random.randint(4, 8)  # Más tareas
        
        # Peso específico para cada instancia
        specific_weight = 1.0 / num_instances
        
        for i in range(1, num_instances + 1):
            name = f"{eval_type} {i}"
            mandatory = True if random.random() > 0.1 else False
            evaluation_instances.append((eval_id, name, specific_weight, mandatory))
    
    for eval_id, name, specific_weight, mandatory in evaluation_instances:
        cursor.execute("""
            INSERT INTO evaluation_instances 
            (evaluation_id, name, specific_weight, mandatory) 
            VALUES (%s, %s, %s, %s)
        """, (eval_id, name, specific_weight, mandatory))
    
    print(f"Se insertaron {len(evaluation_instances)} instancias de evaluación")

def insert_grades(cursor):
    """Insertar notas aleatorias para los estudiantes inscritos"""
    print("Insertando notas...")
    
    # Obtener las inscripciones y las instancias de evaluación correspondientes
    cursor.execute("""
        SELECT e.enrollment_id, ei.instance_eval_id 
        FROM enrollments e 
        JOIN sections s ON e.section_id = s.section_id
        JOIN evaluations ev ON s.section_id = ev.section_id
        JOIN evaluation_instances ei ON ev.evaluation_id = ei.evaluation_id
    """)
    potential_grades = cursor.fetchall()
    
    # Para no sobrecargar la base de datos, seleccionamos un 90% aleatorio (aumentado)
    sample_size = int(len(potential_grades) * 0.9)
    grade_samples = random.sample(potential_grades, sample_size)
    
    grades = []
    for grade_data in grade_samples:
        # Generar una nota aleatoria entre 1.0 y 7.0 con una distribución más realista
        if random.random() < 0.7:  # 70% de notas aprobatorias
            score = round(random.uniform(4.0, 7.0), 1)
        else:
            score = round(random.uniform(1.0, 3.9), 1)
            
        grades.append((grade_data[1], grade_data[0], score))
    
    for instance_eval_id, enrollment_id, score in grades:
        cursor.execute("INSERT INTO grades (instance_eval_id, enrollment_id, score) VALUES (%s, %s, %s)", 
                      (instance_eval_id, enrollment_id, score))
    
    print(f"Se insertaron {len(grades)} notas")

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
        insert_sections(cursor)
        insert_enrollments(cursor)
        insert_evaluations(cursor)
        insert_grades(cursor)
        
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
        
    finally:
        # Cerrar conexiones
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
