GET_INSTANCES_BY_COURSE = """
    SELECT instance_id AS id, year, semester
    FROM course_instances
    WHERE course_id = %s
"""

INSERT_INSTANCE = """
    INSERT INTO course_instances (course_id, year, semester)
    VALUES (%s, %s, %s)
"""

DELETE_INSTANCE = """
    DELETE FROM course_instances WHERE instance_id = %s
"""

UPDATE_INSTANCE = """
    UPDATE course_instances SET year = %s, semester = %s WHERE instance_id = %s
"""

GET_INSTANCE_BY_ID = """
    SELECT instance_id AS id, course_id, year, semester
    FROM course_instances
    WHERE instance_id = %s
"""

GET_ENROLLED_STUDENT_IDS = """
    SELECT student_id FROM enrollments WHERE section_id = %s
"""

GET_TOTAL_WEIGHT_BY_EVALUATION = """
    SELECT SUM(specific_weight) as total_weight
    FROM evaluation_instances
    WHERE evaluation_id = %s
"""

INSERT_EVALUATION_INSTANCE = """
    INSERT INTO evaluation_instances 
    (evaluation_id, name, specific_weight, mandatory) 
    VALUES (%s, %s, %s, %s)
"""

GET_EVALUATION_INSTANCE_DATA = """
    SELECT evaluation_id, specific_weight
    FROM evaluation_instances
    WHERE instance_eval_id = %s
"""

GET_OTHER_TOTAL_WEIGHT = """
    SELECT SUM(specific_weight) as total_weight
    FROM evaluation_instances
    WHERE evaluation_id = %s AND instance_eval_id != %s
"""

UPDATE_EVALUATION_INSTANCE_BASE = """
    UPDATE evaluation_instances SET name = %s, specific_weight = %s
"""

UPDATE_EVALUATION_INSTANCE_WITH_MANDATORY = """
    UPDATE evaluation_instances SET name = %s, specific_weight = %s, mandatory = %s
"""

UPDATE_EVALUATION_INSTANCE_WHERE = """
    WHERE instance_eval_id = %s
"""

COUNT_INSTANCES_BY_EVALUATION = """
    SELECT COUNT(*) as count
    FROM evaluation_instances
    WHERE evaluation_id = %s
"""

REDISTRIBUTE_EVALUATION_WEIGHTS = """
    UPDATE evaluation_instances
    SET specific_weight = %s
    WHERE evaluation_id = %s
"""

CHECK_INSTANCE_EXISTS = """
    SELECT COUNT(*) as count
    FROM course_instances
    WHERE course_id = %s AND year = %s AND semester = %s
"""

CHECK_DUPLICATE_INSTANCE_ON_UPDATE = """
    SELECT COUNT(*) as count
    FROM course_instances
    WHERE course_id = %s AND year = %s AND semester = %s AND instance_id != %s
"""
