
import pytest
from course.models import CourseClass, ScheduleSlot, CourseClassSchedule, Semester, Room, Course
from course.tests.unit_test.test_base import test_app,test_session
from course.dao import check_schedule_conflict

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


def test_check_schedule_conflict_no_result(test_session, monkeypatch, sample_semester, sample_room, sample_course):

    monkeypatch.setattr(
        "course.dao.get_registration_semester",
        lambda: sample_semester
    )

    room = sample_room[0]

    result = check_schedule_conflict(
        test_session,
        room_id=room.id,
        slot_ids=[999]
    )

    assert result is None

def test_check_schedule_conflict_found(test_session, monkeypatch, sample_semester, sample_room):


    monkeypatch.setattr(
        "course.dao.get_registration_semester",
        lambda: sample_semester
    )

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

    result = check_schedule_conflict(
        test_session,
        room_id=sample_room[0].id,
        slot_ids=[1]
    )

    assert result is not None
    assert result.room_id == sample_room[0].id
    assert result.schedule_associations[0].slot_id == slot.id