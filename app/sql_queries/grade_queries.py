GET_SECTION_GRADES = """
    SELECT 
        s.student_id,
        s.name AS student_name,
        e.type AS evaluation_type,
        e.weight AS evaluation_weight,
        ei.name AS evaluation_name,
        ei.specific_weight,
        ei.instance_eval_id,
        g.score
    FROM enrollments en
    JOIN students s ON en.student_id = s.student_id
    JOIN evaluations e ON e.section_id = en.section_id
    JOIN evaluation_instances ei ON ei.evaluation_id = e.evaluation_id
    LEFT JOIN grades g ON g.instance_eval_id = ei.instance_eval_id AND g.enrollment_id = en.enrollment_id
    WHERE en.section_id = %s
    ORDER BY s.name, e.type, ei.name
"""

GET_COURSE_INFO = """
    SELECT 
        c.name as course_name,
        c.code as course_code,
        ci.year,
        ci.semester
    FROM courses c
    JOIN course_instances ci ON c.course_id = ci.course_id
    WHERE c.course_id = %s AND ci.instance_id = %s
"""

GET_ENROLLMENT_ID = """
    SELECT enrollment_id
    FROM enrollments 
    WHERE section_id = %s AND student_id = %s
"""

GET_EXISTING_GRADE = """
    SELECT grade_id
    FROM grades 
    WHERE instance_eval_id = %s AND enrollment_id = %s
"""

INSERT_GRADE = """
    INSERT INTO grades (instance_eval_id, enrollment_id, score) 
    VALUES (%s, %s, %s)
"""

UPDATE_GRADE = """
    UPDATE grades 
    SET score = %s 
    WHERE instance_eval_id = %s AND enrollment_id = %s
"""

GET_ALL_GRADES_FOR_ENROLLMENT = """
    SELECT 
        e.type AS eval_type,
        e.weight AS eval_weight,
        ei.specific_weight,
        g.score
    FROM grades g
    JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
    JOIN evaluations e ON ei.evaluation_id = e.evaluation_id
    WHERE g.enrollment_id = %s
"""