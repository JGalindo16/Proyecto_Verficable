import pytest
from unittest.mock import MagicMock, patch
from app.services.evaluation_instance_service import EvaluationInstanceService


@pytest.fixture
def mock_db():
    with patch("app.services.evaluation_instance_service.DatabaseConnection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.connect.return_value = mock_cursor
        yield mock_cursor


def test_get_instances_by_evaluation(mock_db):
    mock_db.fetchall.return_value = [{"id": 1, "name": "Prueba"}]
    service = EvaluationInstanceService()
    result = service.get_instances_by_evaluation(1)
    assert result == [{"id": 1, "name": "Prueba"}]


def test_get_total_specific_weight_by_evaluation_without_exclude(mock_db):
    mock_db.fetchone.return_value = {"total": 0.6}
    service = EvaluationInstanceService()
    result = service.get_total_specific_weight_by_evaluation(1)
    assert result == 0.6


def test_get_total_specific_weight_by_evaluation_with_exclude(mock_db):
    mock_db.fetchone.return_value = {"total": 0.8}
    service = EvaluationInstanceService()
    result = service.get_total_specific_weight_by_evaluation(1, exclude_instance_id=2)
    assert result == 0.8


def test_add_instance_success(mock_db):
    mock_db.fetchone.side_effect = [{"already_exists": False}, {"section_id": 1}]
    mock_db.fetchall.return_value = [{"enrollment_id": 10}, {"enrollment_id": 11}]
    service = EvaluationInstanceService()
    result = service.add_instance(1, "Instancia X", 0.3, True)
    assert result["success"]


def test_add_instance_duplicate_name(mock_db):
    mock_db.fetchone.return_value = {"already_exists": True}
    service = EvaluationInstanceService()
    result = service.add_instance(1, "Instancia Duplicada", 0.3, True)
    assert not result["success"]
    assert "ya existe" in result["message"].lower()


def test_update_instance_success(mock_db):
    mock_db.fetchone.return_value = None  # No nombre duplicado
    service = EvaluationInstanceService()
    result = service.update_instance(1, 5, "Actualizado", 0.2, False)
    assert result["success"]


def test_update_instance_duplicate_name(mock_db):
    mock_db.fetchone.return_value = {"already_exists": True}
    service = EvaluationInstanceService()
    result = service.update_instance(1, 5, "Repetido", 0.3, True)
    assert not result["success"]
    assert "ya existe" in result["message"].lower()


def test_delete_instance_success(mock_db):
    service = EvaluationInstanceService()
    result = service.delete_instance(1)
    assert result == 200


def test_delete_instance_failure(mock_db):
    mock_db.execute.side_effect = Exception("DB error")
    service = EvaluationInstanceService()
    result = service.delete_instance(99)
    assert result == 400