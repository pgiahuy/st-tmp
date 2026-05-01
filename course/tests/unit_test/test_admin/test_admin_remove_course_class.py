from unittest.mock import patch

import pytest

from course import dao
from course.admin import CourseClassAdmin
from course.exceptions import BusinessException, PermissionDeniedException

from course.models import CourseClass, Registration, Semester, Room, Course, UserRole
from course.services import course_management_service
from course.tests.unit_test.test_base import test_app,test_session, test_client



class FakeAdmin:
    is_authenticated = True
    role = UserRole.ADMIN

class FakeUser:
    is_authenticated = True
    role = UserRole.USER

class FakeUserNotLogin:
    is_authenticated = False
    role = UserRole.USER



@pytest.fixture
def sample_semester(test_session):
    semester = Semester(
        name="HK1",
        year=2026
    )
    test_session.add(semester)
    test_session.commit()
    return semester

@pytest.fixture
def sample_room(test_session):
    room_1 = Room(
        name="A101",
        capacity=50
    )
    room_2 = Room(
        name="A201",
        capacity=50
    )
    test_session.add_all([room_1, room_2])
    test_session.commit()
    return [room_1, room_2]



@pytest.fixture
def sample_course(test_session):
    course_1 = Course(
        course_code="KTPM",
        course_name="Kiểm thử phần mềm",
        credits=3
    )
    course_2 = Course(
        course_code="CNPM",
        course_name="Công nghệ phần mềm",
        credits=3
    )
    test_session.add_all([course_1, course_2])
    test_session.commit()
    return [course_1, course_2]


@pytest.fixture
def sample_course_class(test_session, sample_course, sample_room, sample_semester):
    course_class_1 = CourseClass(
        class_code="KTPM",
        class_index=1,
        course_id=sample_course[0].id,
        semester_id=sample_semester.id,
        max_students=40,
        active=True
    )

    test_session.add(course_class_1)
    test_session.commit()
    return course_class_1

@pytest.fixture
def sample_course_class_none(test_session, sample_course, sample_room, sample_semester):
    course_class_2 = CourseClass(
        class_code="CNPM",
        class_index=1,
        course_id=sample_course[1].id,
        semester_id=sample_semester.id,
        max_students=40,
        active=True
    )
    test_session.add(course_class_2)
    test_session.commit()
    return course_class_2


@pytest.fixture
def sample_registration(test_session, sample_course_class):
    r1 = Registration(course_class_id=sample_course_class.id)
    r2 = Registration(course_class_id=sample_course_class.id)

    test_session.add_all([r1, r2])
    test_session.commit()
    return [r1, r2]


class TestCountCourseRegistrations:

    def test_count_course_registrations_not_exist(self,test_session, sample_course_class):
        count = dao.count_course_registrations( 999)
        assert count == 0

    def test_count_course_registrations_true(self,test_session, sample_registration, sample_course_class):
        count = dao.count_course_registrations( sample_course_class.id)
        assert count == 2

    def test_count_course_registrations_true_zero(self,test_session, sample_registration, sample_course_class_none):
        count = dao.count_course_registrations( sample_course_class_none.id)
        assert count == 0



class TestRemoveCourseClassService:

    def test_delete_course_class_success(self, test_session, sample_course_class_none):
        result = course_management_service.delete_course_class_service(UserRole.ADMIN , sample_course_class_none.id)
        assert result is True
        deleted = dao.get_course_class_by_id(sample_course_class_none.id)
        assert deleted is None

    def test_delete_course_class_has_registration(self, test_session, sample_course_class, sample_registration):
        with pytest.raises(BusinessException):
            course_management_service.delete_course_class_service(UserRole.ADMIN    , sample_course_class.id)

    def test_delete_course_class_not_found(self,test_session):
        with pytest.raises(ValueError) as e:
            course_management_service.delete_course_class_service(UserRole.ADMIN, 9999)
        assert "not found" in str(e)

    def test_delete_course_class_not_permission(self,test_session,sample_course_class):
        with pytest.raises(PermissionDeniedException) as e:
            course_management_service.delete_course_class_service(UserRole.USER, sample_course_class.id)
        assert "quyền" in str(e)



class TestRemoveCourseClassAuth:
    def test_admin_access_allowed(self,monkeypatch):
        monkeypatch.setattr(
            "flask_login.utils._get_user",
            lambda: FakeAdmin()
        )

        view = CourseClassAdmin(CourseClass, None)

        assert view.is_accessible() is True

    def test_admin_access_denied(self,monkeypatch):
        monkeypatch.setattr(
            "flask_login.utils._get_user",
            lambda: FakeUser()
        )
        view = CourseClassAdmin(CourseClass, None)
        assert view.is_accessible() is False

    def test_admin_access_not_logged_in(self,monkeypatch):
        monkeypatch.setattr(
            "flask_login.utils._get_user",
            lambda: FakeUserNotLogin()
        )
        view = CourseClassAdmin(CourseClass, None)
        assert view.is_accessible() is False


def test_create_class_forbidden_v2(monkeypatch,test_client):

    with test_client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True

    monkeypatch.setattr(
        "course.index.render_template",
        lambda *args, **kwargs: ""
    )

    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: type("User", (), {
            "is_authenticated": True,
            "role": UserRole.USER
        })()
    )
    res = test_client.post("/admin/courseclass/delete/")

    assert res.status_code == 403


def test_delete_class_success(test_client, monkeypatch):
    with test_client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True

    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: type("User", (), {
            "is_authenticated": True,
            "role": UserRole.ADMIN
        })()
    )

    res = test_client.post("/admin/courseclass/delete/")

    assert res.status_code == 302
    assert "/admin/courseclass/" in res.location