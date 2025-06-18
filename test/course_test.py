import pytest
from unittest.mock import MagicMock, patch, mock_open
from app.services.course_service import CourseService

@pytest.fixture
def mock_db():
    with patch("app.services.course_service.DatabaseConnection") as mock_db_class:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.connect.return_value = mock_cursor
        mock_db_class.return_value = mock_conn
        yield mock_cursor

def test_add_course_success(mock_db):
    mock_db.fetchone.return_value = {"name_exists": False, "code_exists": False}
    service = CourseService()
    result = service.add_course("Matemáticas", "MAT101")
    assert result["success"] is True

def test_add_course_missing_fields(mock_db):
    service = CourseService()
    result = service.add_course("", "")
    assert not result["success"]
    assert "obligatorios" in result["message"]

def test_add_course_name_exists(mock_db):
    mock_db.fetchone.return_value = {"name_exists": True, "code_exists": False}
    service = CourseService()
    result = service.add_course("Matemáticas", "MAT101")
    assert not result["success"]
    assert "nombre" in result["message"]

def test_add_course_code_exists(mock_db):
    mock_db.fetchone.return_value = {"name_exists": False, "code_exists": True}
    service = CourseService()
    result = service.add_course("Matemáticas", "MAT101")
    assert not result["success"]
    assert "código" in result["message"]

def test_get_all_courses(mock_db):
    mock_db.fetchall.return_value = [{"name": "Física", "code": "FIS101"}]
    service = CourseService()
    result = service.get_all_courses()
    assert isinstance(result, list)
    assert result[0]["code"] == "FIS101"

def test_update_course_success(mock_db):
    mock_db.fetchone.return_value = {"name_exists": False, "code_exists": False}
    service = CourseService()
    result = service.update_course(1, "Biología", "BIO101")
    assert result["success"] is True

def test_update_course_duplicate_name(mock_db):
    mock_db.fetchone.return_value = {"name_exists": True, "code_exists": False}
    service = CourseService()
    result = service.update_course(1, "Biología", "BIO101")
    assert not result["success"]
    assert "nombre" in result["message"]

def test_delete_course_success(mock_db):
    service = CourseService()
    result = service.delete_course(1)
    assert result["success"] is True

def test_delete_all_courses_success(mock_db):
    service = CourseService()
    result = service.delete_all_courses()
    assert result["success"] is True

def test_process_json_success(mock_db):
    json_data = '[{"name": "Química", "code": "QUI101"}]'
    with patch("builtins.open", mock_open(read_data=json_data)):
        with open("fake.json") as file_obj:
            service = CourseService()
            result = service.process_json(file_obj)
            assert result["success"] is True