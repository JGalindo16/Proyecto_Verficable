import pytest
from unittest.mock import patch, MagicMock
from app.services.section_service import SectionService

@pytest.fixture
def mock_db():
    with patch("app.services.section_service.DatabaseConnection") as mock_db_conn:
        mock_instance = MagicMock()
        mock_cursor = MagicMock()
        mock_instance.connect.return_value = mock_cursor
        mock_db_conn.return_value = mock_instance
        yield mock_cursor

def test_get_sections_by_instance(mock_db):
    mock_db.fetchall.return_value = [{"section_id": 1, "number": 1}]
    service = SectionService()
    result = service.get_sections_by_instance(5)
    assert result == [{"section_id": 1, "number": 1}]
    mock_db.execute.assert_called()

def test_add_section_success(mock_db):
    mock_db.fetchone.side_effect = [{"count": 0}, None, None]
    mock_db.lastrowid = 10
    service = SectionService()
    result = service.add_section(1, "2", 5, student_ids=[])
    assert result["success"] is True
    assert result["section_id"] == 10
    mock_db.execute.assert_called()

def test_add_section_duplicate(mock_db):
    mock_db.fetchone.return_value = {"count": 1}
    service = SectionService()
    result = service.add_section(1, "1", 2)
    assert result["success"] is False
    assert "Ya existe una sección" in result["message"]

def test_delete_section_success(mock_db):
    service = SectionService()
    result = service.delete_section(3)
    assert result["success"] is True
    mock_db.execute.assert_called()

def test_update_section_success(mock_db):
    mock_db.fetchone.side_effect = [{"instance_id": 4}, {"count": 0}]
    service = SectionService()
    result = service.update_section(3, 5, 2)
    assert result["success"] is True
    assert "actualizada" in result["message"]

def test_update_section_already_exists(mock_db):
    mock_db.fetchone.side_effect = [
        {"instance_id": 1},
        {"count": 1},
        {"section_id": 99}
    ]
    service = SectionService()
    result = service.update_section(3, 2, 1)
    assert result["success"] is False
    assert "Ya existe otra sección" in result["message"]


def test_get_section_by_id(mock_db):
    mock_db.fetchone.return_value = {"section_id": 3, "number": 1}
    service = SectionService()
    result = service.get_section_by_id(3)
    assert result["section_id"] == 3

def test_get_students_in_section(mock_db):
    mock_db.fetchall.return_value = [{"student_id": 1}]
    service = SectionService()
    result = service.get_students_in_section(4)
    assert result == [{"student_id": 1}]

def test_get_enrolled_student_ids(mock_db):
    mock_db.fetchall.return_value = [{"student_id": 10}, {"student_id": 20}]
    service = SectionService()
    result = service.get_enrolled_student_ids(3)
    assert result == [10, 20]

def test_check_student_enrollment_in_instance(mock_db):
    mock_db.fetchone.return_value = {"name": "Juan"}
    service = SectionService()
    result = service.check_student_enrollment_in_instance(1, 2)
    assert result["name"] == "Juan"