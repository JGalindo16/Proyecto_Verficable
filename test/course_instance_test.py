import pytest
from unittest.mock import patch
from app.services.course_instance_service import CourseInstanceService


@pytest.fixture
def mock_service():
    with patch("app.services.course_instance_service.DatabaseConnection") as MockDB:
        mock_conn = MockDB.return_value
        mock_cursor = mock_conn.connect.return_value
        service = CourseInstanceService()
        yield service, mock_cursor


def test_add_instance_success(mock_service):
    service, cursor = mock_service
    cursor.fetchone.side_effect = [{"count": 0}]
    cursor.lastrowid = 1

    result = service.add_instance(1, 2024, "1")

    assert result["success"] is True


def test_add_instance_duplicate(mock_service):
    service, cursor = mock_service
    cursor.fetchone.return_value = {"count": 1}

    result = service.add_instance(1, 2024, "1")

    assert result["success"] is False
    assert "ya existe" in result["message"].lower()


def test_add_instance_missing_fields(mock_service):
    service, _ = mock_service
    result = service.add_instance(1, None, "")
    assert result["success"] is False
    assert "obligatorios" in result["message"].lower()


def test_delete_instance_success(mock_service):
    service, cursor = mock_service
    cursor.execute.return_value = None

    result = service.delete_instance(1)
    assert result == 200


def test_delete_instance_failure(mock_service):
    service, cursor = mock_service
    cursor.execute.side_effect = Exception("DB Error")

    result = service.delete_instance(1)
    assert result == 400


def test_update_instance_success(mock_service):
    service, cursor = mock_service
    cursor.fetchone.side_effect = [{"course_id": 1}, {"count": 0}]

    result = service.update_instance(1, 2025, "2")

    assert result["success"] is True


def test_update_instance_duplicate(mock_service):
    service, cursor = mock_service
    cursor.fetchone.side_effect = [{"course_id": 1}, {"count": 1}]

    result = service.update_instance(1, 2025, "2")

    assert result["success"] is False
    assert "ya existe" in result["message"].lower()


def test_get_enrolled_student_ids(mock_service):
    service, cursor = mock_service
    cursor.fetchall.return_value = [{"student_id": 101}, {"student_id": 102}]
    result = service.get_enrolled_student_ids(1)

    assert result == [101, 102]


def test_add_evaluation_instance_exceeds_weight(mock_service):
    service, cursor = mock_service
    cursor.fetchone.return_value = {"total_weight": 1}

    result = service.add_evaluation_instance(1, "Test", 0.5)

    assert result["success"] is False
    assert "excede" in result["message"].lower()


def test_redistribute_weights_success(mock_service):
    service, cursor = mock_service
    cursor.fetchone.return_value = {"count": 2}

    result = service.redistribute_weights_after_delete(1)

    assert result["success"] is True


def test_redistribute_weights_empty(mock_service):
    service, cursor = mock_service
    cursor.fetchone.return_value = {"count": 0}

    result = service.redistribute_weights_after_delete(1)

    assert result["success"] is True
    assert "no hay" in result["message"].lower()