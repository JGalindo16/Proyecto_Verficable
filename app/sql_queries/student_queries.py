INSERT_STUDENT = """
    INSERT INTO students (name, email, admission_date)
    VALUES (%s, %s, %s)
"""

SELECT_ALL_STUDENTS = """
    SELECT student_id AS id, name, email, admission_date
    FROM students
"""

SELECT_STUDENT_BY_ID = """
    SELECT student_id AS id, name, email, admission_date
    FROM students
    WHERE student_id = %s
"""

UPDATE_STUDENT = """
    UPDATE students
    SET name = %s, email = %s, admission_date = %s
    WHERE student_id = %s
"""

DELETE_STUDENT = """
    DELETE FROM students
    WHERE student_id = %s
"""

DELETE_ALL_STUDENTS = """
    DELETE FROM students
"""
