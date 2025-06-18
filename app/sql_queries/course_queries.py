CHECK_COURSE_NAME_CODE_EXISTS = """
SELECT 
  EXISTS (SELECT 1 FROM courses WHERE name = %s) AS name_exists,
  EXISTS (SELECT 1 FROM courses WHERE code = %s) AS code_exists;
"""

CHECK_DUPLICATE_COURSE_ON_UPDATE = """
SELECT 
  EXISTS (SELECT 1 FROM courses WHERE name = %s AND course_id != %s) AS name_exists,
  EXISTS (SELECT 1 FROM courses WHERE code = %s AND course_id != %s) AS code_exists;
"""

INSERT_COURSE = "INSERT INTO courses (name, code) VALUES (%s, %s);"

GET_ALL_COURSES = "SELECT course_id AS id, name, code FROM courses;"

GET_COURSE_BY_ID = "SELECT course_id AS id, name, code FROM courses WHERE course_id = %s;"

UPDATE_COURSE = "UPDATE courses SET name = %s, code = %s WHERE course_id = %s;"

DELETE_COURSE = "DELETE FROM courses WHERE course_id = %s;"

DELETE_ALL_COURSES = "DELETE FROM courses;"
