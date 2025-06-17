GET_SECTIONS_BY_INSTANCE = """
    SELECT 
        s.section_id AS id,
        s.number,
        s.professor_id,
        CONCAT('Sección ', s.number) AS name,
        p.name AS professor,
        COUNT(e.enrollment_id) AS student_count
    FROM sections s
    LEFT JOIN professors p ON s.professor_id = p.professor_id
    LEFT JOIN enrollments e ON s.section_id = e.section_id
    WHERE s.instance_id = %s
    GROUP BY s.section_id, p.name
"""

CHECK_DUPLICATE_SECTION_IN_INSTANCE = """
    SELECT COUNT(*) AS count
    FROM sections
    WHERE instance_id = %s AND number = %s
"""

INSERT_SECTION = """
    INSERT INTO sections (instance_id, number, professor_id)
    VALUES (%s, %s, %s)
"""

INSERT_STUDENTS_TO_SECTION = """
    INSERT INTO enrollments (section_id, student_id)
    VALUES (%s, %s)
"""

DELETE_SECTION = """
    DELETE FROM sections
    WHERE section_id = %s
"""

GET_SECTION_BY_ID = """
    SELECT 
        s.section_id AS id,
        s.number,
        s.professor_id,
        s.closed,
        p.name AS professor_name,
        CONCAT('Sección ', s.number) AS name
    FROM sections s
    LEFT JOIN professors p ON s.professor_id = p.professor_id
    WHERE s.section_id = %s
"""

GET_STUDENTS_IN_SECTION = """
    SELECT 
        s.student_id AS id,
        s.name,
        s.email
    FROM enrollments e
    JOIN students s ON e.student_id = s.student_id
    WHERE e.section_id = %s
    ORDER BY s.name
"""

UPDATE_SECTION = """
    UPDATE sections
    SET number = %s, professor_id = %s
    WHERE section_id = %s
"""

DELETE_STUDENTS_FROM_SECTION = """
    DELETE FROM enrollments
    WHERE section_id = %s
"""

GET_ENROLLED_STUDENT_IDS = """
    SELECT student_id
    FROM enrollments
    WHERE section_id = %s
"""

GET_ALL_PROFESSORS = """
    SELECT professor_id AS id, name
    FROM professors
"""

GET_ALL_STUDENTS = """
    SELECT student_id AS id, name
    FROM students
"""

GET_INSTANCE_ID_FROM_SECTION = """
    SELECT instance_id
    FROM sections
    WHERE section_id = %s
"""

CHECK_STUDENT_ALREADY_ENROLLED = """
    SELECT COUNT(*) AS count
    FROM enrollments e
    JOIN sections s ON e.section_id = s.section_id
    WHERE e.student_id = %s
      AND s.instance_id = %s
      AND s.section_id != %s
"""

CHECK_STUDENT_ALREADY_ENROLLED_WITH_NAME = """
    SELECT s.name
    FROM enrollments e
    JOIN students s ON e.student_id = s.student_id
    JOIN sections sec ON e.section_id = sec.section_id
    WHERE s.student_id = %s
      AND sec.instance_id = %s
      AND sec.section_id != %s
    LIMIT 1
"""

CHECK_DUPLICATE_SECTION_NUMBER = """
    SELECT COUNT(*) AS count
    FROM sections
    WHERE section_id != %s AND number = %s
"""