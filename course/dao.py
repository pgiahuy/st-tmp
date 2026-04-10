import hashlib
import re
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from course import db,app
from course.models import User, Student, CourseClass, Registration, Semester, Course, CoursePrerequisite, \
    CourseClassSchedule, SystemConfig, ScheduleSlot, UserRole


def hash_password(password):
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()

def get_user_by_id(id):
    return User.query.get(id)

def get_student_by_id(id):
    return Student.query.filter_by(id=id).first()

def get_student_by_mssv(id):
    return Student.query.filter_by(mssv=id).first()

def get_courses():
    return Course.query.order_by(Course.course_name).all()


def get_course_classes_in_reg_semester(course_id=None, kw=None):

    semester = get_registration_semester()
    if not semester:
        raise Exception('No semester found')

    query = CourseClass.query.filter(
        CourseClass.semester_id == semester.id,
        CourseClass.active == True
    )

    if course_id:
        query = query.filter(CourseClass.course_id == course_id)

    if kw:
        query = query.join(Course).filter(Course.course_name.contains(kw))
    results = query.all()

    return results

def auth_user(username, password, session):
    validate_auth(username, password)

    username = username.strip()
    password = password.strip()

    return session.query(User).filter(
        func.lower(User.username) == username.lower(),
        User.password == hash_password(password)
    ).first()


def validate_auth(username, password):

    if not isinstance(username, str) or not username.strip():
        raise ValueError("Vui lòng nhập tên đăng nhập!")

    if not isinstance(password, str) or not password.strip():
        raise ValueError("Vui lòng nhập mật khẩu!")





def hash_password(password):
    if not password:
        return None
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()




def get_course_class_by_id(id):
    return CourseClass.query.filter_by(id=id).first()

def get_all_course_classes():
    return CourseClass.query.filter(CourseClass.active == True).all()


def get_courses_by_current_reg_semester():
    semester = get_registration_semester()
    if not semester:
        return []
    courses = (db.session.query(Course).join(CourseClass)
               .filter(CourseClass.semester_id == semester.id)
               .distinct().all())
    return courses


def get_config_value(key, default):
    conf = SystemConfig.query.filter_by(key=key).first()
    if conf:
        return int(conf.value)
    return default


def register_course(student_id, course_class_id):
    student = get_student_by_id(student_id)
    course_class = get_course_class_by_id(course_class_id)

    if not course_class or not student:
        raise Exception("Không tìm thấy dữ liệu sinh viên hoặc lớp học.")

    semester = get_registration_semester()
    if not semester:
        raise Exception("Hiện không trong thời gian đăng ký học kỳ!")

    if course_class_is_full(course_class_id):
        raise Exception(f"Lớp {course_class.class_code} đã đầy!")

    conflicting_class = get_conflicting_class(student_id, course_class_id, semester.id)
    if conflicting_class:
        raise Exception(f"Trùng lịch với lớp {conflicting_class.class_code}")

    if check_duplicate_in_semester(student_id, course_class_id):
        raise Exception("Bạn đã đăng ký một lớp khác của môn học này trong học kỳ này rồi!")


    if not check_not_yet_studied(student_id, course_class_id):
        raise Exception("Bạn đã hoàn thành môn học này ở các học kỳ trước!")

    if not check_studied_prerequisites(student_id, course_class_id):
        raise Exception("Chưa hoàn thành môn tiên quyết!")

    max_credits_limit = get_config_value('MAX_CREDITS', 25)

    current_credits = get_total_credits(student, semester.id)
    new_credits = course_class.course.credits

    if current_credits + new_credits > max_credits_limit:
        raise Exception(f"Vượt quá giới hạn {max_credits_limit} tín chỉ/học kỳ!")

    try:
        reg = Registration(
            student_id=student_id,
            course_class_id=course_class_id,
            semester_id=semester.id
        )
        db.session.add(reg)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception("Lỗi hệ thống: " + str(e))

    return {"success": True}


def confirm_registration(student_id):
    student = get_student_by_id(student_id)
    semester = get_registration_semester()

    min_credits_limit = get_config_value('MIN_CREDITS', 12)

    total = get_total_credits(student, semester.id)

    if total < min_credits_limit:
        raise Exception(f"Bạn cần đăng ký tối thiểu {min_credits_limit} tín chỉ để xuất phiếu. (Hiện có: {total})")

    return {"success": True,
            "message": "Xác nhận thành công!"}

def get_course_classes_for_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return []

    semester = get_current_semester()
    registered_classes = db.session.query(CourseClass).join(Registration).filter(
        Registration.student_id == student_id,
        Registration.semester_id == semester.id
    ).options(
        joinedload(CourseClass.schedule_associations).joinedload(CourseClassSchedule.slot)
    ).all()

    return registered_classes

def get_current_semester():
    today = datetime.now()
    return Semester.query.filter(
        Semester.start_date <= today,
        Semester.end_date >= today
    ).first()

def get_registration_semester():
    today = datetime.now().date()
    return (Semester.query.filter(Semester.start_registration_date <= today,
                                 Semester.end_registration_date >= today).first())



def get_total_credits(student, semester_id):
    total = 0
    for reg in student.registrations:
        if reg.semester_id == semester_id:
            if reg.course_class and reg.course_class.course:
                total += reg.course_class.course.credits
    return total


def unregister_course(student_id, course_class_id):
    semester = get_registration_semester()
    reg = Registration.query.filter_by(
        student_id=student_id,
        course_class_id=course_class_id,
        semester_id=semester.id
    ).first()
    if not reg:
        raise Exception("Lớp chưa đăng ký")
    # @minuong check var chỗ này điii
    db.session.delete(reg)
    db.session.commit()


def get_all_student_studied(student_id):
    student = get_student_by_id(student_id)

    reg_semester = get_registration_semester()

    student_studied = []
    for reg in student.registrations:

        if reg_semester and reg.semester_id == reg_semester.id:
            continue

        if reg.course_class and reg.course_class.course:
            student_studied.append(reg.course_class.course.id)

    return set(student_studied)


def check_duplicate_in_semester(student_id, course_class_id):

    semester = get_registration_semester()
    if not semester:
        raise Exception("Không tìm thấy kỳ học hiện tại")

    course_id = get_course_class_by_id(course_class_id).course.id

    student = get_student_by_id(student_id)
    for reg in student.registrations:
        if reg.semester_id != semester.id:
            continue
        existing_course_id = get_course_class_by_id(reg.course_class_id).course.id
        if existing_course_id == course_id:
            return True
    return False



def get_conflicting_class(student_id, course_class_id, reg_semester_id):

    new_class = CourseClass.query.get(course_class_id)
    if not new_class or not reg_semester_id:
        return None

    new_slots = {
        (assoc.slot.weekday, assoc.slot.session)
        for assoc in new_class.schedule_associations if assoc.slot
    }

    registered_registrations = Registration.query.filter_by(
        student_id=student_id,
        semester_id=reg_semester_id
    ).all()

    for reg in registered_registrations:
        old_class = reg.course_class

        if old_class.id == course_class_id:
            continue

        old_slots = {
            (assoc.slot.weekday, assoc.slot.session)
            for assoc in old_class.schedule_associations if assoc.slot
        }

        if new_slots.intersection(old_slots):
            return old_class

    return None


def check_not_yet_studied(student_id, course_class_id):
    student_studied = get_all_student_studied(student_id)
    course = get_course_class_by_id(course_class_id).course

    return course.id not in student_studied


def check_studied_prerequisites(student_id, course_class_id):
    course_class = get_course_class_by_id(course_class_id)
    course = course_class.course

    student_studied = get_all_student_studied(student_id)

    prerequisite_list = CoursePrerequisite.query.filter_by(course_id=course.id).all()
    prerequisite_ids = [pr.prerequisite_id for pr in prerequisite_list]

    if not prerequisite_ids:
        return True

    return all(pr in student_studied for pr in prerequisite_ids)


def course_class_is_full(course_class_id):
    course_class = get_course_class_by_id(course_class_id)
    count = db.session.query(Registration).filter_by(course_class_id=course_class_id).count()
    return count >= course_class.max_students



def change_password(user_id, old_password, new_password):
    user = get_user_by_id(user_id)

    if not user:
        return {"error": "User không tồn tại"}
    print(user)

    if user.password != hash_password(old_password):
        return {"error": "Mật khẩu cũ không đúng"}

    user.password = hash_password(new_password)
    db.session.commit()

    return {"success": True}

def get_courses_by_id(course_id):
    return Course.query.get(course_id)


def check_schedule_conflict(db_session, room_id, slot_ids, current_class_id=None):
    semester_id = get_registration_semester().id
    query = db_session.query(CourseClass).join(
        CourseClassSchedule,
        CourseClass.id == CourseClassSchedule.course_class_id
    ).join(
        ScheduleSlot,
        CourseClassSchedule.slot_id == ScheduleSlot.id
    ).filter(
        CourseClass.room_id == room_id,
        CourseClass.semester_id == semester_id,
        CourseClass.active == True
    )

    if current_class_id:
        query = query.filter(CourseClass.id != current_class_id)

    new_slots = db_session.query(ScheduleSlot).filter(ScheduleSlot.id.in_(slot_ids)).all()

    for ns in new_slots:
        conflict = query.filter(
            ScheduleSlot.weekday == ns.weekday,
            ScheduleSlot.session == ns.session
        ).first()

        if conflict:
            return conflict

    return None