GET_SECCIONES_CON_DATOS = """
    SELECT 
        s.section_id, 
        s.number, 
        p.name AS profesor, 
        c.name AS curso, 
        c.creditos, 
        COUNT(e.enrollment_id) AS inscritos
    FROM sections s
    JOIN course_instances ci ON s.instance_id = ci.instance_id
    JOIN courses c ON ci.course_id = c.course_id
    JOIN professors p ON s.professor_id = p.professor_id
    LEFT JOIN enrollments e ON s.section_id = e.section_id
    GROUP BY s.section_id
"""

GET_SALAS_DISPONIBLES = """
    SELECT classroom_id, name, capacity
    FROM classrooms
"""