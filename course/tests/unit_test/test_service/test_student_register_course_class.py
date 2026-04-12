import pytest

from course import dao
from course.dao import hash_password
from course.services.registration_service import register_course
from course.models import *
from course.tests.unit_test.test_base import test_app,test_session

@pytest.fixture
def sample_student(test_session):
    student = Student(mssv="2351050061",full_name="Phan Gia Huy", email="huy@gmail.com")
    test_session.add(student)
    test_session.commit()
    return student


@pytest.fixture
def sample_user(test_session,sample_student):
    user = User(username="2351050061",password=hash_password("Abc1234@"))
    user.student = sample_student
    test_session.add(user)
    test_session.commit()
    return user




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
        course_code="KTLT",
        course_name="Kĩ thuật lập trình",
        credits=3
    )
    course_2= Course(
        course_code="CNPM",
        course_name="Công nghệ phần mềm",
        credits=3
    )
    test_session.add_all([course_1, course_2])
    test_session.commit()
    return [course_1, course_2]

@pytest.fixture
def sample_course_prerequisite(test_session, sample_course):
    pre = CoursePrerequisite(course_id=sample_course[1].id,prerequisite_id=sample_course[0].id)
    test_session.add(pre)
    test_session.commit()
    return pre


@pytest.fixture
def sample_course_class(test_session, sample_course, sample_room, sample_semester):
    course_class_1 = CourseClass(
        class_code="KTLT",
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
def sample_course_class_need_prerequisite(test_session, sample_course, sample_room, sample_semester):
    course_class_1 = CourseClass(
        class_code="CNPM",
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester.id,
        max_students=40,
        active=True
    )
    test_session.add(course_class_1)
    test_session.commit()
    return course_class_1


def test_register_success(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):

    monkeypatch.setattr(
        "course.dao.get_registration_semester",
        lambda: sample_semester
    )

    res = register_course(sample_student.id, sample_course_class.id)

    assert res["success"] is True

def test_register_fail_missing_prerequisite(
    test_session,
    monkeypatch,
    sample_semester,
    sample_student,
    sample_course_class_need_prerequisite,
    sample_course_prerequisite
):
    monkeypatch.setattr(
        "course.dao.get_registration_semester",
        lambda: sample_semester
    )
    with pytest.raises(Exception):
        register_course(sample_student.id, sample_course_class_need_prerequisite.id)

