import pytest

from course import dao
from course.admin import CourseClassAdmin
from course.exceptions import BusinessException

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
        course_id=sample_course[0].id,
        room_id=sample_room[0].id,
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
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
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
        count = dao.count_course_registrations(test_session, 999)
        assert count == 0

    def test_count_course_registrations_true(self,test_session, sample_registration, sample_course_class):
        count = dao.count_course_registrations(test_session, sample_course_class.id)
        assert count == 2

    def test_count_course_registrations_true_zero(self,test_session, sample_registration, sample_course_class_none):
        count = dao.count_course_registrations(test_session, sample_course_class_none.id)
        assert count == 0



class TestRemoveCourseClassService:

    def test_delete_course_class_success(self, test_session, sample_course_class_none):
        result = course_management_service.delete_course_class_service(test_session, sample_course_class_none.id)
        assert result is True
        deleted = dao.get_course_class_by_id(sample_course_class_none.id)
        assert deleted is None

    def test_delete_course_class_has_registration(self, test_session, sample_course_class, sample_registration):
        with pytest.raises(BusinessException):
            course_management_service.delete_course_class_service(test_session, sample_course_class.id)

    def test_delete_course_class_not_found(self,test_session):
        with pytest.raises(ValueError):
            course_management_service.delete_course_class_service(test_session, 9999)



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

def test_delete_class_forbidden(test_client, monkeypatch):
    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: FakeUser()
    )
    res = test_client.post("/admin/courseclass/delete/")
    assert res.status_code == 403
