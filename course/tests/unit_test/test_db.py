from course import dao
from course.models import User, Student, Course
from course.tests.unit_test.test_base import test_app,test_session,test_client

def test_user_crud(test_session):
    user = User(id=1, username="giahuy", password="123")
    test_session.add(user)
    test_session.commit()

    result = dao.get_user_by_id(1)

    assert result is not None
    assert result.username == "giahuy"


def test_student_by_mssv(test_session):
    student = Student(id=1, mssv="23456789")
    test_session.add(student)
    test_session.commit()

    result = dao.get_student_by_mssv("23456789")

    assert result.id == 1


def test_student_id_by_mssv(test_session):
    student = Student(id=2, mssv="23456789")
    test_session.add(student)
    test_session.commit()

    result = dao.get_student_id_by_mssv("23456789")

    assert result == 2


def test_student_id_by_mssv_not_found(test_session):
    import pytest

    with pytest.raises(AttributeError):
        dao.get_student_id_by_mssv("672816372")


def test_get_courses(test_session):
    c1 = Course(id=1,course_code="MATH101",course_name="Math",credits=3)

    c2 = Course(id=2,course_code="AI101",course_name="AI",credits=4)

    test_session.add_all([c1, c2])
    test_session.commit()

    result = dao.get_courses()

    assert len(result) == 2