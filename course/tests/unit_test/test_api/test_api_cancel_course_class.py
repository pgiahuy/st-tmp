from course.exceptions import BusinessException
from course.tests.unit_test.test_base import test_app,test_client


def login(client, user_id="1"):
    with client.session_transaction() as sess:
        sess["_user_id"] = user_id


def test_cancel_success(test_client, monkeypatch):
    login(test_client)
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
    login(test_client)

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
    login(test_client)
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
    login(test_client)

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
