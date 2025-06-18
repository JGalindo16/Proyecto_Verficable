import pytest
from unittest.mock import patch, MagicMock
from app.services.professor_service import ProfessorService

@pytest.fixture
def mock_db():
    with patch("app.services.professor_service.DatabaseConnection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.connect.return_value = mock_cursor
        yield mock_cursor

def test_add_professor_success(mock_db):
    service = ProfessorService()
    result = service.add_professor("Juan Pérez", "juan@uandes.cl")
    assert result["success"] is True
    mock_db.execute.assert_called_once()

def test_add_professor_failure(mock_db):
    mock_db.execute.side_effect = Exception("DB Error")
    service = ProfessorService()
    result = service.add_professor("Juan Pérez", "juan@uandes.cl")
    assert not result["success"]
    assert "registrar" in result["message"]

def test_get_all_professors(mock_db):
    mock_db.fetchall.return_value = [{"name": "Ana", "email": "ana@uandes.cl"}]
    service = ProfessorService()
    result = service.get_all_professors()
    assert len(result) == 1
    assert result[0]["name"] == "Ana"

def test_get_professor_by_id(mock_db):
    mock_db.fetchone.return_value = {"id": 1, "name": "Carlos"}
    service = ProfessorService()
    result = service.get_professor_by_id(1)
    assert result["name"] == "Carlos"

def test_update_professor_success(mock_db):
    service = ProfessorService()
    result = service.update_professor(1, "María", "maria@uandes.cl")
    assert result["success"] is True
    mock_db.execute.assert_called_once()

def test_update_professor_failure(mock_db):
    mock_db.execute.side_effect = Exception("Fail")
    service = ProfessorService()
    result = service.update_professor(1, "María", "maria@uandes.cl")
    assert not result["success"]
    assert "actualizar" in result["message"]

def test_delete_professor_success(mock_db):
    service = ProfessorService()
    result = service.delete_professor(3)
    assert result["success"] is True
    mock_db.execute.assert_called_once()

def test_delete_professor_failure(mock_db):
    mock_db.execute.side_effect = Exception("Fail")
    service = ProfessorService()
    result = service.delete_professor(3)
    assert not result["success"]
    assert "eliminar el profesor" in result["message"]

def test_delete_all_professors_success(mock_db):
    service = ProfessorService()
    result = service.delete_all_professors()
    assert result["success"] is True

def test_delete_all_professors_failure(mock_db):
    mock_db.execute.side_effect = Exception("Fail")
    service = ProfessorService()
    result = service.delete_all_professors()
    assert not result["success"]
    assert "eliminar todos los profesores" in result["message"]