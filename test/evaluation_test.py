import pytest
from unittest.mock import MagicMock, patch
from app.services.evaluation_service import EvaluationService

@pytest.fixture
def mock_db():
    with patch("app.services.evaluation_service.DatabaseConnection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.connect.return_value = mock_cursor
        yield mock_cursor

def test_add_evaluation_success(mock_db):
    mock_db.fetchone.side_effect = [{"already_exists": False}]
    mock_db.fetchall.return_value = [{"enrollment_id": 1}, {"enrollment_id": 2}]
    service = EvaluationService()
    result = service.add_evaluation(1, "Examen", 0.3, False)
    assert result["success"]

def test_add_evaluation_duplicate_type(mock_db):
    mock_db.fetchone.return_value = {"already_exists": True}
    service = EvaluationService()
    result = service.add_evaluation(1, "Examen", 0.3, False)
    assert not result["success"]
    assert "ya existe" in result["message"].lower()

def test_get_all_evaluations_by_section(mock_db):
    mock_db.fetchall.return_value = [{"type": "Parcial"}, {"type": "Proyecto"}]
    service = EvaluationService()
    result = service.get_all_evaluations_by_section(1)
    assert len(result) == 2
    assert result[0]["type"] == "Parcial"

def test_get_evaluation_by_id(mock_db):
    mock_db.fetchone.return_value = {"id": 3, "type": "Control"}
    service = EvaluationService()
    result = service.get_evaluation_by_id(3)
    assert result["type"] == "Control"

def test_update_evaluation_success(mock_db):
    mock_db.fetchone.return_value = {"already_exists": False}
    service = EvaluationService()
    result = service.update_evaluation(5, "Control Final", 0.5, True)
    assert result["success"]

def test_update_evaluation_duplicate_type(mock_db):
    mock_db.fetchone.return_value = {"already_exists": True}
    service = EvaluationService()
    result = service.update_evaluation(5, "Parcial", 0.5, False)
    assert not result["success"]
    assert "ya existe" in result["message"].lower()

def test_delete_evaluation_success(mock_db):
    service = EvaluationService()
    result = service.delete_evaluation(10)
    assert result["success"]

def test_delete_evaluation_failure(mock_db):
    mock_db.execute.side_effect = Exception("DB Error")
    service = EvaluationService()
    result = service.delete_evaluation(10)
    assert not result["success"]
    assert "error" in result["message"].lower()

def test_get_total_weight_by_section(mock_db):
    mock_db.fetchone.return_value = {"total": 0.95}
    service = EvaluationService()
    result = service.get_total_weight_by_section(1)
    assert result == 0.95

def test_get_total_weight_by_section_none(mock_db):
    mock_db.fetchone.return_value = None
    service = EvaluationService()
    result = service.get_total_weight_by_section(99)
    assert result == 0