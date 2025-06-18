CHECK_EMAIL_EXISTS = "SELECT 1 FROM students WHERE email = %s"

INSERT_STUDENT_WITH_ID = """
    INSERT INTO students (student_id, name, email, admission_date)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email)
"""

INSERT_STUDENT = """
    INSERT INTO students (name, email, admission_date)
    VALUES (%s, %s, %s)
"""

INSERT_PROFESSOR_WITH_ID = """
    INSERT INTO professors (professor_id, name, email)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email)
"""

INSERT_PROFESSOR = """
    INSERT INTO professors (name, email)
    VALUES (%s, %s)
"""

INSERT_COURSE_WITH_ID = """
    INSERT INTO courses (course_id, code, name, creditos)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE code = VALUES(code), name = VALUES(name), creditos = VALUES(creditos)
"""

INSERT_COURSE = """
    INSERT INTO courses (code, name, creditos)
    VALUES (%s, %s, %s)
"""

SELECT_PREREQUISITE_ID_BY_CODE = "SELECT course_id FROM courses WHERE code = %s"

INSERT_COURSE_PREREQUISITE = """
    INSERT IGNORE INTO course_prerequisites (course_id, prerequisite_id)
    VALUES (%s, %s)
"""

CHECK_COURSE_EXISTS = "SELECT 1 FROM courses WHERE course_id = %s"

INSERT_INSTANCE_WITH_ID = """
    INSERT INTO course_instances (instance_id, course_id, year, semester)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE course_id=VALUES(course_id), year=VALUES(year), semester=VALUES(semester)
"""

INSERT_INSTANCE = """
    INSERT INTO course_instances (course_id, year, semester)
    VALUES (%s, %s, %s)
"""

CHECK_SECTION_EXISTS = "SELECT 1 FROM sections WHERE section_id = %s"

CHECK_STUDENT_EXISTS = "SELECT 1 FROM students WHERE student_id = %s"

INSERT_ENROLLMENT = """
    INSERT INTO enrollments (student_id, section_id)
    VALUES (%s, %s)
"""

INSERT_CLASSROOM_WITH_ID = """
    INSERT INTO classrooms (classroom_id, name, capacity)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE name = VALUES(name), capacity = VALUES(capacity)
"""

INSERT_CLASSROOM = """
    INSERT INTO classrooms (name, capacity)
    VALUES (%s, %s)
"""

CHECK_INSTANCE_EXISTS = "SELECT 1 FROM course_instances WHERE instance_id = %s"

CHECK_PROFESSOR_EXISTS = "SELECT 1 FROM professors WHERE professor_id = %s"

INSERT_SECTION = """
    INSERT INTO sections (instance_id, number, professor_id)
    VALUES (%s, %s, %s)
"""

INSERT_EVALUATION = """
    INSERT INTO evaluations (section_id, type, weight, optional)
    VALUES (%s, %s, %s, %s)
"""

INSERT_EVALUATION_INSTANCE = """
    INSERT INTO evaluation_instances (evaluation_id, name, specific_weight, mandatory)
    VALUES (%s, %s, %s, %s)
"""

SELECT_INSTANCE_EVAL_AND_SECTION = """
    SELECT ei.instance_eval_id, e.section_id
    FROM evaluation_instances ei
    JOIN evaluations e ON ei.evaluation_id = e.evaluation_id
    WHERE e.evaluation_id = %s AND ei.name LIKE %s
"""

SELECT_ENROLLMENT_ID = """
    SELECT enrollment_id FROM enrollments
    WHERE student_id = %s AND section_id = %s
"""

INSERT_GRADE = """
    INSERT INTO grades (enrollment_id, instance_eval_id, score)
    VALUES (%s, %s, %s)
"""
