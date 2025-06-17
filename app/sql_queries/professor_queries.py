GET_ALL_PROFESSORS = """
    SELECT professor_id AS id, name, email
    FROM professors
"""

GET_PROFESSOR_BY_ID = """
    SELECT professor_id AS id, name, email
    FROM professors
    WHERE professor_id = %s
"""

INSERT_PROFESSOR = """
    INSERT INTO professors (name, email)
    VALUES (%s, %s)
"""

UPDATE_PROFESSOR = """
    UPDATE professors
    SET name = %s, email = %s
    WHERE professor_id = %s
"""

DELETE_PROFESSOR = """
    DELETE FROM professors
    WHERE professor_id = %s
"""