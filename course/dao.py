import hashlib
from datetime import datetime

from course import db
from course.models import User, Student, CourseClass, Registration, Semester, Course, CoursePrerequisite


def hash_password(password):
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()

def get_user_by_id(id):
    return User.query.get(id)

def get_student_by_id(id):
    return Student.query.filter_by(id=id).first()

def get_student_by_mssv(id):
    return Student.query.filter_by(mssv=id).first()

def auth_user(username, password, session):
    if not username or username is None:
        raise Exception("Vui lòng nhập tên đăng nhập!")
    if not password or password is None:
        raise Exception("Vui lòng nhập mật khẩu!")
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return session.query(User).filter_by(username=username, password=password).first()

def get_course_class_by_id(id):
    return CourseClass.query.filter_by(id=id).first()

def get_all_course_classes():
    return CourseClass.query.filter(CourseClass.active == True).all()

def register_course(student_id, course_class_id):

    student = get_student_by_id(student_id)
    course_class = get_course_class_by_id(course_class_id)
    if not course_class:
        return {"success": False, "message": "Không tìm thấy lớp học phần"}, 400
    if not student:
        raise Exception("Sinh viên không tồn tại!")

    if course_class_is_full(course_class_id):
        raise Exception("Lớp đã đầy!")

    if not check_schedule_not_conflict(student_id, course_class_id):
        raise Exception("Trùng lịch học!")

    if not check_not_yet_studied(student_id, course_class_id):
        raise Exception("Không được đăng ký môn đã học!")

    if not check_studied_prerequisites(student_id, course_class_id):
        raise Exception("Chưa học xong các môn tiên quyết!")

    semester = get_current_semester()
    print("semester = ", semester.id)
    reg = Registration(student_id=student_id, course_class_id=course_class_id,
                       semester_id=2)

    db.session.add(reg)
    db.session.commit()

    return {"student_id": student_id, "class_id": course_class_id}

def confirm_registration(student_id):

    student = get_student_by_id(student_id)
    semester = get_current_semester()

    total = get_total_credits(student, semester.id)

    if total < semester.min_credits:
        raise Exception(f"Chưa đủ {semester.min_credits} tín chỉ")

    db.session.commit()


def get_current_semester():
    today = datetime.now()
    return Semester.query.filter(
        Semester.start_date <= today,
        # Semester.end_date >= today
    ).first()

def get_total_credits(student, semester):
    total = 0
    for reg in student.registrations:
        if reg.semester_id == semester.id:
            total += reg.class_section.course.credits
    return total

def unregister_course(student_id, course_class_id):
    pass





def get_all_student_studied(student_id, current_semester_id=None):
    student = get_student_by_id(student_id)
    student_studied = []
    for reg in student.registrations:

        if current_semester_id and reg.semester_id == current_semester_id:
            continue

        course_class = CourseClass.query.filter_by(id=reg.course_class_id).first()
        if not course_class:
            continue

        course = Course.query.filter_by(id=course_class.course_id).first()
        if not course:
            continue

        student_studied.append(course.id)

    return set(student_studied)


def check_schedule_not_conflict(student_id, course_class_id):

    new_class = CourseClass.query.get(course_class_id)
    semester_id = get_current_semester().id

    student = get_student_by_id(student_id)
    registered_classes = [
        reg.course_class for reg in student.registrations
        if reg.semester_id == semester_id
    ]

    for new_slot in new_class.schedule_slots:
        for clazz in registered_classes:

            for slot in clazz.schedule_slots:
                if new_slot.weekday == slot.weekday and new_slot.session == slot.session:
                    return False
    return True

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



