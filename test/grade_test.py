import pytest
from unittest.mock import patch, MagicMock
from app.services.grade_service import GradeService

@pytest.fixture
def mock_db():
    with patch("app.services.grade_service.DatabaseConnection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.connect.return_value = mock_cursor
        yield mock_cursor

def test_get_section_grades(mock_db):
    mock_db.fetchall.return_value = [{"student_id": 1, "score": 6.0}]
    service = GradeService()
    result = service.get_section_grades(1)
    assert len(result) == 1
    assert result[0]["score"] == 6.0

def test_get_course_info_for_grades(mock_db):
    mock_db.fetchone.return_value = {"course_name": "Matemática"}
    service = GradeService()
    result = service.get_course_info_for_grades(1, 2)
    assert result["course_name"] == "Matemática"

def test_create_or_update_grade_insert(mock_db):
    mock_db.fetchone.side_effect = [
        {"enrollment_id": 10},  
        None,                   
        {"eval_type": "Parcial", "eval_weight": 0.5, "specific_weight": 1.0, "score": 6.0}
    ]
    mock_db.fetchall.return_value = [
        {"eval_type": "Parcial", "eval_weight": 0.5, "specific_weight": 1.0, "score": 6.0},
        {"eval_type": "Control", "eval_weight": 0.5, "specific_weight": 1.0, "score": 7.0}
    ]
    service = GradeService()
    result = service.create_or_update_grade(1, 2, 3, 6.0)
    assert result["success"]
    assert result["type_average"] == 7.0
    assert result["final_average"] == 6.5

def test_create_or_update_grade_update(mock_db):
    mock_db.fetchone.side_effect = [
        {"enrollment_id": 20},     
        {"grade_id": 5},           
        {"eval_type": "Tarea", "eval_weight": 1.0, "specific_weight": 1.0, "score": 5.0}
    ]
    mock_db.fetchall.return_value = [
        {"eval_type": "Tarea", "eval_weight": 1.0, "specific_weight": 1.0, "score": 5.0}
    ]
    service = GradeService()
    result = service.create_or_update_grade(1, 1, 1, 5.0)
    assert result["success"]
    assert result["type_average"] == 5.0
    assert result["final_average"] == 5.0

def test_create_or_update_grade_no_enrollment(mock_db):
    mock_db.fetchone.return_value = None  
    service = GradeService()
    result = service.create_or_update_grade(1, 999, 1, 5.0)
    assert result[0] is False
    assert "Inscripción" in result[1]

def test_create_or_update_grade_calc_empty_grades(mock_db):
    mock_db.fetchone.side_effect = [
        {"enrollment_id": 100},
        {"grade_id": 1}
    ]
    mock_db.fetchall.return_value = []
    service = GradeService()
    result = service.create_or_update_grade(1, 1, 1, 4.0)
    assert result[0] is True
    assert result[1] == "Nota actualizada correctamente"
    assert result[2] == 0.0
    assert result[3] == 0.0

def test_create_or_update_grade_db_error(mock_db):
    mock_db.execute.side_effect = Exception("DB Fail")
    service = GradeService()
    result = service.create_or_update_grade(1, 1, 1, 5.0)
    assert not result["success"]
    assert result["type_average"] is None