import pytest
from unittest.mock import patch, MagicMock
from app.services.student_service import StudentService
from app.alertas.students_alerts import *

@pytest.fixture
def mock_db():
    with patch("app.services.student_service.DatabaseConnection") as mock_db_conn:
        mock_instance = MagicMock()
        mock_cursor = MagicMock()
        mock_instance.connect.return_value = mock_cursor
        mock_db_conn.return_value = mock_instance
        yield mock_cursor

def test_add_student_success(mock_db):
    service = StudentService()
    result = service.add_student("Ana", "ana@example.com", "2023-03-01")
    assert result["success"] is True
    assert result["message"] == ESTUDIANTE_CREADO_EXITOSAMENTE
    mock_db.execute.assert_called()

def test_add_student_error(mock_db):
    mock_db.execute.side_effect = Exception("DB error")
    service = StudentService()
    result = service.add_student("Ana", "ana@example.com", "2023-03-01")
    assert result["success"] is False
    assert result["message"] == ERROR_AL_CREAR_ESTUDIANTE

def test_get_all_students(mock_db):
    mock_db.fetchall.return_value = [{"id": 1, "name": "Ana"}]
    service = StudentService()
    result = service.get_all_students()
    assert result == [{"id": 1, "name": "Ana"}]
    mock_db.execute.assert_called()

def test_get_student_by_id(mock_db):
    mock_db.fetchone.return_value = {"id": 1, "name": "Ana"}
    service = StudentService()
    result = service.get_student_by_id(1)
    assert result["name"] == "Ana"
    mock_db.execute.assert_called()

def test_update_student_success(mock_db):
    service = StudentService()
    result = service.update_student(1, "Ana", "ana@new.com", "2024-01-01")
    assert result["success"] is True
    assert result["message"] == ESTUDIANTE_ACTUALIZADO_EXITOSAMENTE

def test_update_student_error(mock_db):
    mock_db.execute.side_effect = Exception("DB error")
    service = StudentService()
    result = service.update_student(1, "Ana", "ana@new.com", "2024-01-01")
    assert result["success"] is False
    assert result["message"] == ERROR_AL_ACTUALIZAR_ESTUDIANTE

def test_delete_student_success(mock_db):
    service = StudentService()
    result = service.delete_student(1)
    assert result["success"] is True
    assert result["message"] == ESTUDIANTE_ELIMINADO_EXITOSAMENTE

def test_delete_student_error(mock_db):
    mock_db.execute.side_effect = Exception("DB error")
    service = StudentService()
    result = service.delete_student(1)
    assert result["success"] is False
    assert result["message"] == ERROR_AL_ELIMINAR_ESTUDIANTE

def test_delete_all_students_success(mock_db):
    service = StudentService()
    result = service.delete_all_students()
    assert result["success"] is True
    assert result["message"] == TODOS_LOS_ESTUDIANTES_ELIMINADOS

def test_delete_all_students_error(mock_db):
    mock_db.execute.side_effect = Exception("DB error")
    service = StudentService()
    result = service.delete_all_students()
    assert result["success"] is False
    assert result["message"] == ERROR_AL_ELIMINAR_TODOS