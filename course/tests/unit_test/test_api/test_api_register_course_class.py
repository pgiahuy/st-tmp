import pytest
from course.tests.unit_test.test_base import test_app, test_client
from flask_login import utils
from course.models import UserRole


@pytest.fixture()
def mock_current_user(monkeypatch):
    user = type("User", (), {
        "id": 1,
        "username": "2351050061",
        "role": UserRole.USER,
        "is_authenticated": True
    })()
    monkeypatch.setattr(utils, "_get_user", lambda: user)


@pytest.fixture()
def mock_current_user_un_auth(monkeypatch):
    user = type("User", (), {
        "id": 1,
        "username": "2351050061",
        "role": UserRole.USER,
        "is_authenticated": False
    })()
    monkeypatch.setattr(utils, "_get_user", lambda: user)


def test_register_course_success(test_client, monkeypatch, mock_current_user):
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


def test_register_course_fail_un_auth(test_client, monkeypatch, mock_current_user_un_auth):
    monkeypatch.setattr("course.dao.get_student_id_by_mssv", lambda m: 1)
    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.register_course",
        lambda semester_id, student_id, course_class_id: None
    )

    res = test_client.post("/api/course-register", json={
        "course_class_id": 1
    })

    assert res.status_code == 401
    assert res.json["success"] is False


def test_register_course_exception(test_client, monkeypatch, mock_current_user):
    monkeypatch.setattr("course.dao.get_student_id_by_mssv", lambda m: 1)
    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.register_course",
        lambda *args, **kwargs: (_ for _ in ()).throw(Exception("lỗi"))
    )

    res = test_client.post("/api/course-register", json={
        "course_class_id": 1
    })

    assert res.status_code == 400
    assert res.json["success"] is False
    assert "lỗi" in res.json["message"]


def test_register_course_missing_data(test_client, mock_current_user):
    res = test_client.post("/api/course-register", json={})

    assert res.status_code == 400
    assert res.json["success"] is False


def test_register_course_student_not_found(test_client, monkeypatch, mock_current_user):
    monkeypatch.setattr("course.dao.get_student_id_by_mssv", lambda m: None)

    res = test_client.post("/api/course-register", json={
        "course_class_id": 1
    })

    assert res.status_code == 400
    assert "không tồn tại" in res.json["message"]


def test_confirm_register_success(test_client, monkeypatch, mock_current_user):
    monkeypatch.setattr("course.dao.get_student_by_mssv", lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.confirm_registration",
        lambda semester_id, student_id: None
    )

    res = test_client.post("/api/register-course/confirm")

    assert res.status_code == 200
    assert res.json["success"] is True


def test_confirm_register_fail_un_auth(test_client, monkeypatch, mock_current_user_un_auth):
    monkeypatch.setattr("course.dao.get_student_by_mssv", lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())


    res = test_client.post("/api/register-course/confirm")

    assert res.status_code == 401
    assert res.json["success"] is False


def test_confirm_register_student_not_found(test_client, monkeypatch, mock_current_user):
    monkeypatch.setattr("course.dao.get_student_id_by_mssv", lambda m: None)
    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())


    res = test_client.post("/api/register-course/confirm")

    assert res.status_code == 400
    assert res.json["success"] is False
    assert "Sinh viên không" in res.json["message"]


def test_confirm_register_fail_semester_not_found(test_client, monkeypatch, mock_current_user):
    monkeypatch.setattr("course.dao.get_student_by_mssv", lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester", lambda: None)


    res = test_client.post("/api/register-course/confirm")

    assert res.status_code == 400
    assert res.json["success"] is False
    assert "Không có học kỳ" in res.json["message"]


def test_confirm_register_fail_exception(test_client, monkeypatch, mock_current_user):
    monkeypatch.setattr("course.dao.get_student_by_mssv", lambda m: type("S", (), {"id": 1})())

    monkeypatch.setattr("course.dao.get_registration_semester", lambda: type("S", (), {"id": 1})())

    monkeypatch.setattr(
        "course.services.registration_service.confirm_registration",
        lambda *args, **kwargs: (_ for _ in ()).throw(Exception("lỗi"))
    )



    res = test_client.post("/api/register-course/confirm")

    assert res.status_code == 400
    assert res.json["success"] is False
    assert "lỗi" in res.json["message"]

