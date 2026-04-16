import pytest
from flask_login import login_manager
from pytest_mock import mocker

from course.models import UserRole

from course.tests.unit_test.test_base import test_app,test_client

def login(client, user_id="1"):
    with client.session_transaction() as sess:
        sess["_user_id"] = user_id


class FakeAdmin:
    is_authenticated = True
    role = UserRole.ADMIN

class FakeUser:
    username = '2351050061'
    is_authenticated = True
    role = UserRole.ADMIN

class FakeUserNotLogin:
    is_authenticated = False
    role = UserRole.USER

def test_register_course_success(test_client, monkeypatch):
    login(test_client)

    monkeypatch.setattr("course.dao.get_student_id_by_mssv", lambda m: 1)
    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.register_course",
        lambda semester_id, student_id, course_class_id: None
    )

    res = test_client.post("/api/course-register", json={
        "course_class_id": 1
    })

    assert res.status_code == 200
    assert res.json["success"] is True


def test_register_course_missing_data(test_client):
    login(test_client)

    res = test_client.post("/api/course-register", json={})

    assert res.status_code == 400
    assert res.json["success"] is False


def test_register_course_student_not_found(test_client, monkeypatch):
    login(test_client)

    monkeypatch.setattr("course.dao.get_student_id_by_mssv", lambda m: None)

    res = test_client.post("/api/course-register", json={
        "course_class_id": 1
    })

    assert res.status_code == 400
    assert "không tồn tại" in res.json["message"]


def test_confirm_register_success(test_client, monkeypatch):
    login(test_client)

    monkeypatch.setattr("course.dao.get_student_by_mssv", lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.confirm_registration",
        lambda semester_id,student_id: None
    )

    res = test_client.post("/api/register-course/confirm")

    assert res.status_code == 200
    assert res.json["success"] is True