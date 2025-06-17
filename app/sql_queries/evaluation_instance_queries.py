GET_INSTANCES_BY_EVALUATION = """
    SELECT instance_eval_id AS id, name, specific_weight, mandatory
    FROM evaluation_instances
    WHERE evaluation_id = %s
"""

GET_TOTAL_WEIGHT = """
    SELECT COALESCE(SUM(specific_weight), 0) AS total
    FROM evaluation_instances
    WHERE evaluation_id = %s
"""

GET_TOTAL_WEIGHT_EXCLUDE = """
    SELECT COALESCE(SUM(specific_weight), 0) AS total
    FROM evaluation_instances
    WHERE evaluation_id = %s AND instance_eval_id != %s
"""

INSERT_EVALUATION_INSTANCE = """
    INSERT INTO evaluation_instances (evaluation_id, name, specific_weight, mandatory)
    VALUES (%s, %s, %s, %s)
"""

GET_SECTION_ID_BY_EVALUATION = """
    SELECT section_id FROM evaluations WHERE evaluation_id = %s
"""

GET_ENROLLMENTS_BY_SECTION = """
    SELECT enrollment_id FROM enrollments WHERE section_id = %s
"""

BULK_INSERT_GRADES = """
    INSERT INTO grades (instance_eval_id, enrollment_id, score)
    VALUES (%s, %s, %s)
"""

UPDATE_INSTANCE = """
    UPDATE evaluation_instances
    SET name = %s, specific_weight = %s, mandatory = %s
    WHERE instance_eval_id = %s
"""

DELETE_INSTANCE = """
    DELETE FROM evaluation_instances
    WHERE instance_eval_id = %s
"""

CHECK_DUPLICATE_NAME_ON_CREATE = """
    SELECT COUNT(*) > 0 AS already_exists
    FROM evaluation_instances
    WHERE evaluation_id = %s AND name = %s
"""

CHECK_DUPLICATE_NAME_ON_UPDATE = """
    SELECT 1
    FROM evaluation_instances
    WHERE evaluation_id = %s AND name = %s AND instance_eval_id != %s
    LIMIT 1
"""