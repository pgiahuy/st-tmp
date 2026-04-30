import pytest

from course import dao
from course.models import User, Student, Course, Semester, Room, CourseClass, ScheduleSlot, Session, Day
from course.tests.unit_test.test_base import test_app,test_session,test_client
from course.services.registration_service import register_course
@pytest.fixture
def sample_student(test_session):
    student = Student(mssv="2351050061",full_name="Phan Gia Huy", email="huy@gmail.com")
    test_session.add(student)
    test_session.commit()
    return student



@pytest.fixture
def sample_semester(test_session):
    s1 = Semester(
        name="HK1",
        year=2026
    )
    s2 = Semester(
        name="HK2",
        year=2026
    )
    test_session.add_all([s1,s2])
    test_session.commit()
    return [s1,s2]

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

# @pytest.fixture
# def sample_course_prerequisite(test_session, sample_course):
#     pre = CoursePrerequisite(course_id=sample_course[1].id,prerequisite_id=sample_course[0].id)
#     test_session.add(pre)
#     test_session.commit()
#     return pre

# hk1 - room[0]
@pytest.fixture
def sample_course_class(test_session, sample_course, sample_room, sample_semester):
    c1 = CourseClass(
        class_code="KTLT01",
        class_index = 1,
        course_id=sample_course[0].id,
        room_id=sample_room[0].id,
        semester_id=sample_semester[0].id,
        max_students=40,
        active=True
    )
    c2 = CourseClass(
        class_code="KTLT02",
        class_index=2,
        course_id=sample_course[0].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester[0].id,
        max_students=40,
        active=True
    )
    c3 = CourseClass(
        class_code="CNPM01",
        class_index=1,
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester[0].id,
        max_students=40,
        active=True
    )
    c4 = CourseClass(
        class_code="CNPM02",
        class_index=1,
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester[1].id,
        max_students=40,
        active=True
    )
    c5 = CourseClass(
        class_code="CNPM03",
        class_index=2,
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester[1].id,
        max_students=40,
        active=False
    )

    test_session.add_all([c1,c2,c3,c4])
    test_session.commit()
    return [c1,c2,c3,c4]

#
#
# # hk1 - room[1]
# @pytest.fixture
# def sample_course_class_full_slot(test_session, sample_course, sample_room, sample_semester):
#     course_class_1 = CourseClass(
#         class_code="CNPM",
#         course_id=sample_course[1].id,
#         room_id=sample_room[1].id,
#         semester_id=sample_semester[0].id,
#         max_students=0,
#         active=True
#     )
#
#     test_session.add(course_class_1)
# #     test_session.commit()
# #     return course_class_1
#
#
# @pytest.fixture
# def sample_course_class_need_prerequisite(test_session, sample_course, sample_room, sample_semester):
#     course_class_1 = CourseClass(
#         class_code="CNPM",
#         course_id=sample_course[1].id,
#         room_id=sample_room[1].id,
#         semester_id=sample_semester[1].id,
#         max_students=40,
#         active=True
#     )
#     test_session.add(course_class_1)
#     test_session.commit()
#     return course_class_1


def test_get_course_class_ids_student_registered(sample_course_class, sample_student, sample_semester):
    register_course(sample_semester[0].id,sample_student.id, sample_course_class[0].id)
    res = dao.get_course_class_ids_student_registered(sample_semester[0].id, sample_student.id)
    assert res == [sample_course_class[0].id]
    assert dao.get_course_class_by_id(res[0]) == sample_course_class[0]
    assert dao.get_course_class_by_id(res[0]).class_code == "KTLT01"

def test_get_course_classes_in_reg_semester(sample_semester, sample_course_class):
    res = dao.get_course_classes_in_reg_semester(sample_semester[0].id)
    assert sample_semester[0].id == res[0].semester_id
    assert sample_semester[0].id == res[1].semester_id

def test_get_course_classes_in_reg_semester_have_course_id(sample_semester, sample_course_class, sample_course):
    res = dao.get_course_classes_in_reg_semester(sample_semester[0].id,course_id=sample_course[0].id)
    assert sample_semester[0].id == res[0].semester_id
    assert sample_semester[0].id == res[1].semester_id
    assert res[0].course_id == sample_course[0].id
    assert res[1].course_id == sample_course[0].id
    assert len(res) == 2


def test_get_course_classes_in_reg_semester_have_kw(sample_semester, sample_course_class, sample_course):
    res = dao.get_course_classes_in_reg_semester(sample_semester[0].id,kw= "Công")
    assert sample_semester[0].id == res[0].semester_id
    assert res[0].course_id == sample_course[1].id
    assert res[0].course.course_name == "Công nghệ phần mềm"
    assert len(res) == 1


def test_get_course_class_ids_student_registered_none(sample_semester, sample_student):
    res = dao.get_course_class_ids_student_registered(sample_semester[0].id, sample_student.id  )
    assert res == []

def test_get_all_course_classes(sample_course_class):
    res = dao.get_all_course_classes()
    assert len(res) == 4


def test_get_conflicting_class(sample_student,sample_course_class):
    res = dao.get_conflicting_class(sample_student.id,sample_course_class[0].id)
    assert res is None

def test_get_courses_by_current_reg_semester_1(sample_semester, sample_course_class):
    res = dao.get_courses_by_current_reg_semester(sample_semester[0].id)
    assert len(res) == 2

def test_get_courses_by_current_reg_semester_2(sample_semester, sample_course_class):
    res = dao.get_courses_by_current_reg_semester(sample_semester[1].id)
    assert len(res) == 1