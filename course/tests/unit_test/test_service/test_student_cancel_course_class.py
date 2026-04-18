import datetime

import pytest
from sqlalchemy import Date

from course import dao
from course.dao import auth_user, hash_password, count_course_registrations
from course.exceptions import PermissionDeniedException, BusinessException
from course.models import User, Semester, Course, CourseClass, Student, Registration, RegistrationStatus
from course.services import registration_service
from course.services.registration_service import cancel_registration
from course.tests.unit_test.test_base import test_app,test_session


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



# hk1 - room[0]
@pytest.fixture
def sample_course_class(test_session, sample_course, sample_semester):
    course_class_1 = CourseClass(
        class_code="KTLT",
        course_id=sample_course[0].id,
        room_id=11,
        semester_id=sample_semester[0].id,
        max_students=40,
        active=True
    )

    test_session.add(course_class_1)
    test_session.commit()
    return course_class_1

@pytest.fixture
def sample_registration(test_session, sample_student, sample_course_class, sample_semester):
    reg = Registration(
        student_id=sample_student.id,
        course_class_id=sample_course_class.id,
        semester_id=sample_semester[0].id,
    )

    test_session.add(reg)
    test_session.commit()
    return reg


class TestStudentCancelCourseClassService:
    def test_cancel_success(self,sample_semester,sample_student,sample_course_class, sample_registration):
        is_true = registration_service.cancel_registration(sample_semester[0].id
                                                           ,sample_student.id, sample_course_class.id)
        assert  is_true is True

    def test_cancel_fail_not_registered(self,sample_semester,sample_student,sample_registration):
        with pytest.raises(BusinessException) as e:
            registration_service.cancel_registration(sample_semester[0].id, sample_student.id, 11)

        assert "chưa đăng ký" in str(e.value)

    def test_cancel_fail_after_2_weeks(self,sample_semester,sample_student,sample_course_class,sample_registration):
        semester = dao.get_semester_by_id(sample_registration.semester_id)
        semester.start_date = datetime.date.today() - datetime.timedelta(weeks=2 )

        with pytest.raises(BusinessException) as e:
            cancel_registration(sample_registration.semester_id, sample_student.id, sample_course_class.id)
        assert "sau 2 tuần" in str(e.value)

    def test_cancel_fail_after_midterm_test(self,sample_semester,sample_student,sample_course_class,sample_registration):
        sample_registration.is_midterm_tested = True
        with pytest.raises(BusinessException) as e:
            cancel_registration(sample_registration.semester_id, sample_student.id, sample_course_class.id)
        assert "đã thi giữa kỳ" in str(e.value)