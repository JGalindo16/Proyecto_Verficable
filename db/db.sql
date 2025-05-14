-- Eliminar todo si ya existe (para desarrollo)
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS evaluation_instances;
DROP TABLE IF EXISTS evaluations;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS course_instances;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS courses;

-- =============================
-- Tabla: courses
-- =============================
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) NOT NULL,
    descripcion TEXT DEFAULT NULL,
    creditos INT DEFAULT NULL
);

-- =============================
-- Tabla: professors
-- =============================
CREATE TABLE professors (
    professor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- =============================
-- Tabla: course_instances
-- =============================
CREATE TABLE course_instances (
    instance_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    year INT NOT NULL,
    semester VARCHAR(10) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: sections
-- =============================
CREATE TABLE sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    instance_id INT NOT NULL,
    number INT NOT NULL,
    professor_id INT NOT NULL,
    FOREIGN KEY (instance_id) REFERENCES course_instances(instance_id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professors(professor_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: students
-- =============================
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    admission_date DATE NOT NULL
);

-- =============================
-- Tabla: enrollments
-- =============================
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: evaluations
-- =============================
CREATE TABLE evaluations (
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL,
    type VARCHAR(255) NOT NULL,
    weight FLOAT NOT NULL,
    optional BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: evaluation_instances
-- =============================
CREATE TABLE evaluation_instances (
    instance_eval_id INT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    specific_weight FLOAT NOT NULL,
    mandatory BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: grades
-- =============================
CREATE TABLE grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    instance_eval_id INT NOT NULL,
    enrollment_id INT NOT NULL,
    score FLOAT NOT NULL CHECK (score BETWEEN 1.0 AND 7.0),
    FOREIGN KEY (instance_eval_id) REFERENCES evaluation_instances(instance_eval_id) ON DELETE CASCADE,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: course_prerequisites
-- =============================
CREATE TABLE course_prerequisites (
    course_id INT NOT NULL,
    prerequisite_id INT NOT NULL,
    PRIMARY KEY (course_id, prerequisite_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: classrooms
-- =============================
CREATE TABLE classrooms (
    classroom_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    capacity INT NOT NULL
);
