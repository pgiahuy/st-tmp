import pytest
from flask_login import utils

from course.exceptions import BusinessException
from course.models import UserRole
from course.tests.unit_test.test_base import test_app,test_client

@pytest.fixture(autouse=True)
def mock_current_user(monkeypatch):

    user = type("User", (), {
        "id": 1,
        "username": "2351050061",
        "role": UserRole.USER,
        "is_authenticated": True
    })()
    monkeypatch.setattr(utils, "_get_user", lambda: user)



def test_cancel_success(test_client, monkeypatch):
    monkeypatch.setattr("course.dao.get_student_by_mssv", lambda m: type("S", (), {"id": 1})())
    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.cancel_registration",
        lambda semester_id, student_id, course_class_id: None
    )

    res = test_client.delete("/api/course-register/1")

    assert res.status_code == 200
    assert res.json["success"] is True


def test_cancel_fail_unregistered(test_client, monkeypatch):

    monkeypatch.setattr("course.dao.get_student_by_mssv",
                         lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester",
                         lambda: type("S", (), {"id": 1})())
    monkeypatch.setattr(
        "course.services.registration_service.cancel_registration",
        lambda *args, **kwargs: (_ for _ in ()).throw(BusinessException("Chưa đăng ký"))
    )
    res = test_client.delete("/api/course-register/1")

    assert res.status_code == 400
    assert "Chưa đăng ký" in res.json["message"]


def test_cancel_fail_after_2_week(test_client, monkeypatch):
    monkeypatch.setattr("course.dao.get_student_by_mssv",
                        lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester",
                        lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.cancel_registration",
        lambda *args, **kwargs: (_ for _ in ()).throw(BusinessException)
    )
    res = test_client.delete("/api/course-register/1")

    assert res.status_code == 400


def test_cancel_fail_middle_term(test_client, monkeypatch):

    monkeypatch.setattr("course.dao.get_student_by_mssv",
                        lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester",
                        lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.cancel_registration",
        lambda *args, **kwargs: (_ for _ in ()).throw(BusinessException)
    )

    res = test_client.delete("/api/course-register/1")

    assert res.status_code == 400
