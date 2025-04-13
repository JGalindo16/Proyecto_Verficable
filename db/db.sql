-- Eliminar todo si ya existe (para desarrollo)
DROP TABLE IF EXISTS Grade;
DROP TABLE IF EXISTS EvaluationInstance;
DROP TABLE IF EXISTS Evaluation;
DROP TABLE IF EXISTS Enrollment;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Section;
DROP TABLE IF EXISTS CourseInstance;
DROP TABLE IF EXISTS Professor;
DROP TABLE IF EXISTS Course;

-- =============================
-- Tabla: Course
-- =============================
CREATE TABLE Course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) NOT NULL
);

-- =============================
-- Tabla: Professor
-- =============================
CREATE TABLE Professor (
    professor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- =============================
-- Tabla: CourseInstance
-- =============================
CREATE TABLE CourseInstance (
    instance_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    year INT NOT NULL,
    semester VARCHAR(10) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: Section
-- =============================
CREATE TABLE Section (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    instance_id INT NOT NULL,
    number INT NOT NULL,
    professor_id INT NOT NULL,
    FOREIGN KEY (instance_id) REFERENCES CourseInstance(instance_id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES Professor(professor_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: Student
-- =============================
CREATE TABLE Student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    admission_date DATE NOT NULL
);

-- =============================
-- Tabla: Enrollment
-- =============================
CREATE TABLE Enrollment (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    section_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES Section(section_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: Evaluation
-- =============================
CREATE TABLE Evaluation (
    evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL,
    type VARCHAR(255) NOT NULL,
    weight FLOAT NOT NULL,
    optional BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (section_id) REFERENCES Section(section_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: EvaluationInstance
-- =============================
CREATE TABLE EvaluationInstance (
    instance_eval_id INT AUTO_INCREMENT PRIMARY KEY,
    evaluation_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    specific_weight FLOAT NOT NULL,
    mandatory BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (evaluation_id) REFERENCES Evaluation(evaluation_id) ON DELETE CASCADE
);

-- =============================
-- Tabla: Grade
-- =============================
CREATE TABLE Grade (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    instance_eval_id INT NOT NULL,
    enrollment_id INT NOT NULL,
    score FLOAT NOT NULL CHECK (score BETWEEN 1.0 AND 7.0),
    FOREIGN KEY (instance_eval_id) REFERENCES EvaluationInstance(instance_eval_id) ON DELETE CASCADE,
    FOREIGN KEY (enrollment_id) REFERENCES Enrollment(enrollment_id) ON DELETE CASCADE
);