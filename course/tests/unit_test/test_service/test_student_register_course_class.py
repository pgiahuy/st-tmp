from datetime import timedelta

import pytest
from course.dao import hash_password
from course.exceptions import BusinessException
from course.services.registration_service import register_course, confirm_registration
from course.models import *
from course.tests.unit_test.test_base import test_app,test_session

class FakeUser:
    is_authenticated = True

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

@pytest.fixture
def sample_course_prerequisite(test_session, sample_course):
    pre = CoursePrerequisite(course_id=sample_course[1].id,prerequisite_id=sample_course[0].id)
    test_session.add(pre)
    test_session.commit()
    return pre

# hk1 - room[0]
@pytest.fixture
def sample_course_class(test_session, sample_course, sample_room, sample_semester):
    course_class_1 = CourseClass(
        class_code="KTLT",
        course_id=sample_course[0].id,
        room_id=sample_room[0].id,
        semester_id=sample_semester[0].id,
        max_students=40,
        active=True
    )

    test_session.add(course_class_1)
    test_session.commit()
    return course_class_1



# hk1 - room[1]
@pytest.fixture
def sample_course_class_full_slot(test_session, sample_course, sample_room, sample_semester):
    course_class_1 = CourseClass(
        class_code="CNPM",
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester[0].id,
        max_students=0,
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
        semester_id=sample_semester[1].id,
        max_students=40,
        active=True
    )
    test_session.add(course_class_1)
    test_session.commit()
    return course_class_1

@pytest.fixture
def sample_schedule_slots(test_session):
    slot1 = ScheduleSlot(weekday=Day.MONDAY, session=Session.MORNING)

    test_session.add(slot1)
    test_session.commit()

    return slot1




@pytest.fixture
def sample_course_class_conflict_1(test_session, sample_course, sample_room, sample_semester):
    course_class_1 = CourseClass(
        class_code="KTLT",
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester[0].id,
        max_students=50,
        active=True
    )

    test_session.add(course_class_1)
    test_session.commit()
    return course_class_1

@pytest.fixture
def sample_course_class_conflict_2(test_session, sample_course, sample_room, sample_semester):
    course_class_1 = CourseClass(
        class_code="CNPM",
        course_id=sample_course[1].id,
        room_id=sample_room[1].id,
        semester_id=sample_semester[0].id,
        max_students=50,
        active=True
    )

    test_session.add(course_class_1)
    test_session.commit()
    return course_class_1

@pytest.fixture
def sample_course_class_schedule(test_session, sample_course_class_conflict_1, sample_course_class_conflict_2, sample_schedule_slots):
    assoc1 = CourseClassSchedule(
        course_class_id=sample_course_class_conflict_1.id,
        slot_id=sample_schedule_slots.id
    )
    assoc2 = CourseClassSchedule(
        course_class_id=sample_course_class_conflict_2.id,
        slot_id=sample_schedule_slots.id
    )
    test_session.add_all([assoc1, assoc2])
    test_session.commit()

    return [assoc1, assoc2]
# =========

def test_register_success(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):

    res = register_course(sample_semester[0].id ,sample_student.id, sample_course_class.id)
    assert res is True

def test_register_confirm_success(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    monkeypatch.setattr(
        "course.dao.get_config_value",
        lambda key, default=None: 3 if key == ConfigEnum.MIN_CREDITS else default
    )
    register_course(sample_semester[0].id,sample_student.id,sample_course_class.id)
    res = confirm_registration(sample_semester[0].id ,sample_student.id)
    assert res is True



def test_register_fail_not_semester(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    with pytest.raises(BusinessException) as e:
        res = register_course(11 ,sample_student.id, sample_course_class.id)
    assert "học kỳ" in str(e.value)

def test_register_fail_missing_prerequisite(test_session,monkeypatch,sample_semester,sample_student,
                                            sample_course_class_need_prerequisite,sample_course_prerequisite):

    with pytest.raises(BusinessException) as e:
        register_course(sample_semester[0].id, sample_student.id, sample_course_class_need_prerequisite.id)
    assert "Chưa hoàn thành môn tiên quyết" in str(e.value)
    assert "KTLT" in str(e.value)

def test_register_fail_registered(test_session,monkeypatch,sample_semester, sample_student, sample_course_class):

     register_course(sample_semester[0].id, sample_student.id, sample_course_class.id)

     with pytest.raises(BusinessException) as e:
         register_course(sample_semester[0].id, sample_student.id, sample_course_class.id)
     assert "Bạn đã đăng ký một lớp khác của môn học này trong học kỳ này rồi!" in str(e.value)


def test_register_fail_studied(test_session,monkeypatch,sample_semester, sample_student, sample_course_class):
    # HK1

    register_course(sample_semester[0].id, sample_student.id, sample_course_class.id)

    with pytest.raises(BusinessException) as e:#HK2
        register_course(sample_semester[1].id, sample_student.id, sample_course_class.id)
    assert "Bạn đã hoàn thành môn học này ở các học kỳ trước!" in str(e.value)

def test_register_fail_max_credit(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    monkeypatch.setattr(
        "course.dao.get_config_value",
        lambda key, default=None: 2 if key == ConfigEnum.MAX_CREDITS else default
    )

    with pytest.raises(BusinessException) as e:
        register_course(sample_semester[0].id, sample_student.id, sample_course_class.id)
    assert "Vượt quá giới hạn" in str(e.value)

def test_register_equal_max_credit(monkeypatch, sample_semester, sample_student, sample_course_class):

    monkeypatch.setattr(
        "course.dao.get_config_value",
        lambda k, d=None: 3 if k == ConfigEnum.MAX_CREDITS else d
    )
    res = register_course(sample_semester[0].id, sample_student.id, sample_course_class.id)

    assert res is True

def test_register_fail_min_credit(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    monkeypatch.setattr(
        "course.dao.get_config_value",
        lambda key, default=None: 12 if key == ConfigEnum.MIN_CREDITS else default
    )

    register_course(sample_semester[0].id,sample_student.id,sample_course_class.id)
    with pytest.raises(BusinessException) as e:
        confirm_registration(sample_semester[0].id ,sample_student.id)
    assert "tối thiểu" in str(e.value)





def test_register_fail_full_slot(test_session, monkeypatch, sample_semester, sample_student, sample_course_class_full_slot):

    with pytest.raises(BusinessException) as e:
        register_course(sample_semester[0].id, sample_student.id, sample_course_class_full_slot.id)
    assert "đã đầy" in str(e.value)

def test_register_conflict(test_session, monkeypatch, sample_semester, sample_student,sample_course_class_schedule,
                           sample_course_class_conflict_1, sample_course_class_conflict_2):

    register_course(sample_semester[0].id, sample_student.id, sample_course_class_conflict_1.id)

    with pytest.raises(BusinessException) as e:
        register_course(sample_semester[0].id, sample_student.id, sample_course_class_conflict_2.id)
    assert "Trùng lịch" in str(e.value)


def test_register_fail_class_not_found(sample_student, sample_semester):
    with pytest.raises(ValueError):
        register_course(sample_semester[0].id, sample_student.id, 999)


def test_register_fail_student_not_found(sample_course_class, sample_semester):
    with pytest.raises(ValueError):
        register_course(sample_semester[0].id, 999, sample_course_class.id)


def test_register_fail_inactive_class(test_session,monkeypatch, sample_course, sample_room, sample_semester, sample_student):
    cls = CourseClass(
        class_code="WEB",
        course_id=sample_course[0].id,
        room_id=sample_room[0].id,
        semester_id=sample_semester[0].id,
        max_students=40,
        active=False
    )

    test_session.add(cls)
    test_session.commit()
    with pytest.raises(ValueError) as e:
        register_course(sample_semester[0].id, sample_student.id, cls.id)

    assert "không mở" in str(e.value)


def test_register_after_deadline(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    semester = sample_course_class.semester

    semester.end_registration_date = datetime.now() - timedelta(days=1)
    test_session.commit()

    with pytest.raises(BusinessException) as e:
        register_course(sample_semester[0].id, sample_student.id, sample_course_class.id)

    assert "Không được đăng ký sau thời gian đăng ký môn" in str(e.value)

def test_register_before_deadline(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    semester = sample_course_class.semester

    semester.end_registration_date = datetime.now() + timedelta(days=1)
    test_session.commit()
    result = register_course(sample_semester[0].id,sample_student.id,sample_course_class.id)
    assert result is True

def test_register_at_deadline(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    semester = sample_course_class.semester

    semester.end_registration_date = datetime.now()
    test_session.commit()
    result = register_course(sample_semester[0].id,sample_student.id,sample_course_class.id)
    assert result is True


def test_register_before_open(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    semester = sample_course_class.semester

    semester.start_registration_date = datetime.now() + timedelta(days=1)
    test_session.commit()

    with pytest.raises(BusinessException) as e:
        register_course(semester.id, sample_student.id, sample_course_class.id)

    assert "Không được đăng ký trước thời gian đăng ký môn" in str(e.value)


def test_register_no_deadline(test_session, monkeypatch, sample_semester, sample_student, sample_course_class):
    result = register_course(sample_semester[0].id,sample_student.id,sample_course_class.id)
    assert result is True