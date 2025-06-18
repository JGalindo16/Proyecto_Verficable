# app/sql_queries/report_queries.py

GET_SECCION_CERRADA = """
    SELECT closed FROM sections WHERE section_id = %s
"""

GET_FINAL_GRADES_POR_ENROLLMENT = """
    SELECT e.enrollment_id, SUM(g.score * ei.specific_weight) AS nota_final
    FROM enrollments e
    JOIN grades g ON g.enrollment_id = e.enrollment_id
    JOIN evaluation_instances ei ON ei.instance_eval_id = g.instance_eval_id
    JOIN evaluations ev ON ev.evaluation_id = ei.evaluation_id
    WHERE ev.section_id = %s
    GROUP BY e.enrollment_id
"""

GET_STUDENT_ID_FROM_ENROLLMENT = """
    SELECT student_id FROM enrollments WHERE enrollment_id = %s
"""

INSERT_NOTA_FINAL = """
    INSERT INTO final_grades (section_id, student_id, final_score)
    VALUES (%s, %s, %s)
"""

UPDATE_SECTION_CERRADA = """
    UPDATE sections SET closed = TRUE WHERE section_id = %s
"""

GET_REPORTE_POR_EVALUACION = """
    SELECT st.student_id, st.name AS student_name,
           ev.evaluation_id, ev.type AS eval_type, ev.weight AS eval_weight,
           ei.name AS instance_name, ei.specific_weight, g.score
    FROM students st
    JOIN enrollments e ON st.student_id = e.student_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
    JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
    WHERE ev.section_id = %s
    ORDER BY st.name, ev.evaluation_id, ei.instance_eval_id
"""

GET_REPORTE_NOTAS_FINALES = """
    SELECT st.student_id, st.name AS student_name,
           ev.evaluation_id, ev.weight AS eval_weight,
           g.score, ei.specific_weight
    FROM students st
    JOIN enrollments e ON st.student_id = e.student_id
    JOIN grades g ON g.enrollment_id = e.enrollment_id
    JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
    JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
    WHERE ev.section_id = %s
    ORDER BY st.name, ev.evaluation_id, ei.instance_eval_id
"""

GET_CERTIFICADO_POR_ALUMNO = """
    SELECT st.name AS student_name, c.name AS course_name, c.code,
           ev.evaluation_id, ev.type AS eval_type, ev.weight AS eval_weight,
           ei.name AS instance_name, ei.specific_weight, g.score
    FROM students st
    JOIN enrollments e ON st.student_id = e.student_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
    JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
    JOIN sections s ON ev.section_id = s.section_id
    JOIN course_instances ci ON s.instance_id = ci.instance_id
    JOIN courses c ON ci.course_id = c.course_id
    WHERE s.section_id = %s AND st.student_id = %s
    ORDER BY ev.evaluation_id, ei.instance_eval_id
"""

GET_RESUMEN_POR_ESTUDIANTE = """
    SELECT st.name AS student_name, c.name AS course_name, c.code,
           ev.evaluation_id, ev.type AS eval_type, ev.weight AS eval_weight,
           ei.name AS instance_name, ei.specific_weight, g.score
    FROM students st
    JOIN enrollments e ON st.student_id = e.student_id
    JOIN sections s ON e.section_id = s.section_id
    JOIN grades g ON e.enrollment_id = g.enrollment_id
    JOIN evaluation_instances ei ON g.instance_eval_id = ei.instance_eval_id
    JOIN evaluations ev ON ei.evaluation_id = ev.evaluation_id
    JOIN course_instances ci ON s.instance_id = ci.instance_id
    JOIN courses c ON ci.course_id = c.course_id
    WHERE st.student_id = %s AND s.closed = TRUE
    ORDER BY c.name, ev.evaluation_id, ei.instance_eval_id
"""
