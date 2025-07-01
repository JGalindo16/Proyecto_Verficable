INSERT_EVALUATION = """
    INSERT INTO evaluations (section_id, type, weight, optional)
    VALUES (%s, %s, %s, %s)
"""

INSERT_DEFAULT_INSTANCE = """
    INSERT INTO evaluation_instances (evaluation_id, name, specific_weight, mandatory)
    VALUES (%s, %s, %s, %s)
"""

GET_ENROLLMENTS_BY_SECTION = """
    SELECT enrollment_id
    FROM enrollments
    WHERE section_id = %s
"""

BULK_INSERT_INITIAL_GRADES = """
    INSERT INTO grades (instance_eval_id, enrollment_id, score)
    VALUES (%s, %s, %s)
"""

GET_ALL_BY_SECTION = """
    SELECT evaluation_id AS id, type, weight, optional
    FROM evaluations
    WHERE section_id = %s
"""

GET_BY_ID = """
    SELECT evaluation_id AS id, type, weight, optional, section_id
    FROM evaluations
    WHERE evaluation_id = %s
"""

UPDATE_EVALUATION = """
    UPDATE evaluations
    SET type = %s, weight = %s, optional = %s
    WHERE evaluation_id = %s
"""

DELETE_EVALUATION = """
    DELETE FROM evaluations
    WHERE evaluation_id = %s
"""

GET_TOTAL_WEIGHT_BY_SECTION = """
    SELECT COALESCE(SUM(weight), 0) AS total
    FROM evaluations
    WHERE section_id = %s
"""

CHECK_DUPLICATE_TYPE_ON_CREATE = """
    SELECT COUNT(*) > 0 AS already_exists
    FROM evaluations
    WHERE section_id = %s AND type = %s
"""

CHECK_DUPLICATE_TYPE_ON_UPDATE = """
    SELECT COUNT(*) > 0 AS already_exists
    FROM evaluations
    WHERE type = %s AND evaluation_id != %s AND section_id = (
        SELECT section_id FROM evaluations WHERE evaluation_id = %s
    )
"""
