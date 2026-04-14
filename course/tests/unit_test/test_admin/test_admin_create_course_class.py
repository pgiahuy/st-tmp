
import pytest

from course.admin import CourseClassAdmin
from course.exceptions import BusinessException
from course.models import CourseClass, ScheduleSlot, CourseClassSchedule, Semester, Room, Course, UserRole
from course.services.course_management_service import validate_course_class
from course.tests.unit_test.test_base import test_app,test_session,test_client


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
        capacity=40
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

def test_check_schedule_no_conflict(test_session, monkeypatch, sample_semester, sample_room, sample_course):
    room_id = sample_room[0].id

    slot_1 = ScheduleSlot(
        id=1,
        weekday="TUESDAY",
        session="MORNING"
    )
    slot_2 = ScheduleSlot(
        id=2,
        weekday="MONDAY",
        session="MORNING"
    )

    course_class = CourseClass(
        id=1,
        room_id=room_id,
        semester_id=sample_semester.id,
        active=True
    )

    mapping = CourseClassSchedule(
        course_class=course_class,
        slot=slot_1
    )

    test_session.add_all([slot_1,slot_2, course_class, mapping])
    test_session.commit()



    result = validate_course_class(
        semester_id=sample_semester.id,
        room_id=room_id,
        slot_ids=[slot_2.id],
        max_students= 50,
        course_class_id= None
    )

    assert result is None



def test_check_schedule_conflict_no_result(test_session, monkeypatch, sample_semester, sample_room, sample_course):


    room = sample_room[0]

    result = validate_course_class(
        semester_id=sample_semester.id,
        room_id=room.id,
        slot_ids=[999],
        max_students= 50,
        course_class_id= None
    )

    assert result is None

def test_check_schedule_conflict_found(test_session, monkeypatch, sample_semester, sample_room):


    slot = ScheduleSlot(
        id=1,
        weekday="MONDAY",
        session="MORNING"
    )

    course_class = CourseClass(
        id=1,
        room_id=sample_room[0].id,
        semester_id=sample_semester.id,
        active=True
    )

    mapping = CourseClassSchedule(
        course_class=course_class,
        slot=slot
    )

    test_session.add_all([slot, course_class, mapping])
    test_session.commit()

    result = validate_course_class(
        semester_id=sample_semester.id,
        room_id=sample_room[0].id,
        slot_ids=[1],
        max_students=50,
        course_class_id=None
    )
    assert result is not None

    conflict = result["conflict"]
    slot = result["slot"]

    assert conflict.room_id == sample_room[0].id
    assert any(a.slot_id == slot.id for a in conflict.schedule_associations)

def test_fail_max_slots(test_session, monkeypatch, sample_semester, sample_room):
    with pytest.raises(BusinessException) as e:
        validate_course_class(
            semester_id=sample_semester.id,room_id=sample_room[0].id,
            slot_ids=[1],max_students=51,course_class_id=None
        )

    assert "Số sinh viên tối đa là" in str(e.value)


def test_fail_max_room_capacity(test_session, monkeypatch, sample_semester, sample_room):
    with pytest.raises(BusinessException) as e:
        validate_course_class(
            semester_id=sample_semester.id,room_id=sample_room[1].id,
            slot_ids=[1],max_students=44,course_class_id=None
        )

    assert "Số sinh viên tối đa là" in str(e.value)


class TestCreateCourseClassAuth:
    def test_admin_access_allowed(self, monkeypatch):
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



def test_create_class_forbidden(test_client, monkeypatch):
    monkeypatch.setattr(
        "flask_login.utils._get_user",
        lambda: FakeUser()
    )
    res = test_client.get("/admin/courseclass/new/")
    assert res.status_code == 403