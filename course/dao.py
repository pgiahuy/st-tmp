import hashlib
import string
from datetime import datetime, timedelta, date
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from course import db
from course.models import User, Student, CourseClass, Registration, Semester, Course, CoursePrerequisite, \
    CourseClassSchedule, SystemConfig, ScheduleSlot, Room, RegistrationStatus, ConfigEnum


def hash_password(password = None):
    if not password:
        return None
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()

def get_user_by_id(id):
    return db.session.get(User, id)

def get_student_by_id(id):
    return Student.query.filter_by(id=id).first()

def get_student_by_mssv(id):
    return Student.query.filter_by(mssv=id).first()
def get_student_id_by_mssv(mssv):
    return Student.query.filter_by(mssv=mssv).first().id

def get_courses():
    return Course.query.order_by(Course.course_name).all()

def get_course_classes_student_registered(semester_id, student_id):
    regis = Registration.query.filter_by(semester_id=semester_id, student_id=student_id, status = RegistrationStatus.REGISTERED).all()
    if not regis:
        return []
    regis_ids = [reg.course_class_id for reg in regis ]

    return CourseClass.query.filter(CourseClass.id.in_(regis_ids)).all()

def get_course_class_ids_student_registered(semester_id, student_id):
    regis = Registration.query.filter_by(semester_id=semester_id, student_id=student_id, status = RegistrationStatus.REGISTERED).all()
    if not regis:
        return []
    return [reg.course_class_id for reg in regis ]

def get_course_classes_in_reg_semester(semester_id= None, course_id=None, kw=None):

    query = CourseClass.query.filter(
        CourseClass.semester_id == semester_id,
        CourseClass.active == True
    )

    if course_id:
        query = query.filter(CourseClass.course_id == course_id)

    if kw:
        query = query.join(Course).filter(Course.course_name.contains(kw))
    results = query.all()

    return results

def auth_user(username, password):
    validate_auth(username, password)

    username = username.strip()
    password = password.strip()

    return db.session.query(User).filter(
        func.lower(User.username) == username.lower(),
        User.password == hash_password(password)
    ).first()


def validate_auth(username, password):

    if not isinstance(username, str) or not username.strip():
        raise ValueError("Vui lòng nhập tên đăng nhập!")

    if not isinstance(password, str) or not password.strip():
        raise ValueError("Vui lòng nhập mật khẩu!")


def get_course_class_by_id(id):
    return CourseClass.query.filter_by(id=id).first()

def get_all_course_classes():
    return CourseClass.query.filter(CourseClass.active == True).all()


def get_conflicting_class(student_id, course_class_id, reg_semester_id =  None):

    new_class = db.session.get(CourseClass, course_class_id)
    if not new_class or not reg_semester_id:
        return None


    new_slots = {
        (assoc.slot.weekday, assoc.slot.session)
        for assoc in new_class.schedule_associations if assoc.slot
    }


    registered_registrations = Registration.query.filter_by(
        student_id=student_id,
        semester_id=reg_semester_id,
        status = RegistrationStatus.REGISTERED
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


def check_not_yet_studied(semester_id ,student_id, course_class_id):
    student_studied = get_all_student_studied(semester_id, student_id)
    course = get_course_class_by_id(course_class_id).course

    return course.id not in student_studied



def course_class_is_full(course_class_id):
    course_class = get_course_class_by_id(course_class_id)
    count = db.session.query(Registration).filter_by(course_class_id=course_class_id, status = RegistrationStatus.REGISTERED).count()
    return count >= course_class.max_students

# all môn trong kì
def get_courses_by_current_reg_semester(semester_id=None):

    courses = (db.session.query(Course).join(CourseClass)
               .filter(CourseClass.semester_id == semester_id)
               .distinct().all())
    return courses


def get_config_value(key, default=None):
    conf = SystemConfig.query.filter_by(key=key.value).first()
    return int(conf.value) if conf else default

def check_student_enough_credits_in_semester(semester_id , student_id):

    total = get_total_credits(student_id,semester_id)
    if total >= get_config_value(ConfigEnum.MIN_CREDITS, 12):
        return True

    return False


# def get_course_classes_for_student(student_id):
#     student = get_student_by_id(student_id)
#     if not student:
#         return []
#
#     semester = get_current_semester()
#     registered_classes = db.session.query(CourseClass).join(Registration).filter(
#         Registration.student_id == student_id,
#         Registration.semester_id == semester.id
#     ).options(
#         joinedload(CourseClass.schedule_associations).joinedload(CourseClassSchedule.slot)
#     ).all()

    # return registered_classes

def get_current_semester():
    today = date.today()
    return Semester.query.filter(
        Semester.start_date <= today,
        Semester.end_date >= today
    ).first()

def get_registration_semester():
    now = date.today()
    return (Semester.query.filter(Semester.start_registration_date <= now,
                                 Semester.end_registration_date >= now).first())


def get_total_credits(student_id, semester_id):
    total = 0
    registered_classes = get_course_classes_student_registered(semester_id, student_id)
    for course_class in registered_classes:
        if course_class.semester_id == semester_id and course_class.course:
            total += course_class.course.credits
    return total


# def unregister_course(student_id, course_class_id):
#     semester = get_registration_semester()
#     reg = Registration.query.filter_by(
#         student_id=student_id,
#         course_class_id=course_class_id,
#         semester_id=semester.id
#     ).first()
#     if not reg:
#         raise Exception("Lớp chưa đăng ký")
#     # @minuong check var chỗ này điii
#     db.session.delete(reg)
#     db.session.commit()
#
def get_registration(student_id, course_class_id, semester_id):
    return Registration.query.filter_by(
        student_id=student_id,
        course_class_id=course_class_id,
        semester_id=semester_id
    ).first()


def student_cancel_registration(reg):
    reg.pre_status = reg.status
    reg.status = RegistrationStatus.STUDENT_CANCELLED
    reg.updated_at = datetime.now()
    db.session.commit()

def system_cancel_registration(reg):
    if reg.status == RegistrationStatus.REGISTERED:
        reg.pre_status = reg.status
        reg.status = RegistrationStatus.SYSTEM_CANCELLED

def get_semester_by_id(semester_id):
    return Semester.query.filter_by(id=semester_id).first()

def get_all_student_studied(semester_id , student_id):
    student = get_student_by_id(student_id)
    semester = get_semester_by_id(semester_id)
    student_studied = []
    for reg in student.registrations:

        if semester and reg.semester_id == semester_id:
            continue

        if reg.course_class and reg.course_class.course and reg.status == RegistrationStatus.REGISTERED:
            student_studied.append(reg.course_class.course.id)

    return set(student_studied)



def check_duplicate_in_semester(semester_id ,student_id, course_class_id):

    course_id = get_course_class_by_id(course_class_id).course.id
    student_registered = get_course_classes_student_registered(semester_id,student_id)
    
    for c in student_registered:
        existing_course_id = c.course.id
        if existing_course_id == course_id:
            return True
    return False


def get_prerequisites_not_yet_study(semester_id, student_id, course_class_id):
    course_class = get_course_class_by_id(course_class_id)
    course = course_class.course

    #list(id)
    student_studied = get_all_student_studied(semester_id ,student_id)

    prerequisite_list = CoursePrerequisite.query.filter_by(course_id=course.id).all()
    prerequisite_ids = [pr.prerequisite_id for pr in prerequisite_list]

    missing = [pr for pr in prerequisite_ids if pr not in student_studied]
    return missing


def change_password(user_id, new_password):
    user = db.session.get(User, user_id)

    user.password = hash_password(new_password)

    db.session.commit()

#
# def get_courses_by_id(course_id):
#     return Course.query.get(course_id)

def get_room_by_id(room_id):
    return db.session.get(Room,room_id)

def check_schedule_conflict(  semester_id, room_id, slot_ids, current_class_id=None):

    query = db.session.query(CourseClass).join(
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

    if current_class_id: # by_pass khi update
        query = query.filter(CourseClass.id != current_class_id)

    new_slots = db.session.query(ScheduleSlot).filter(ScheduleSlot.id.in_(slot_ids)).all()

    for ns in new_slots:
        conflict = query.filter(
            ScheduleSlot.weekday == ns.weekday,
            ScheduleSlot.session == ns.session
        ).first()

        if conflict:
            return conflict

    return None


def count_course_registrations( course_class_id):
    return db.session.query(Registration).filter_by(course_class_id=course_class_id, status = RegistrationStatus.REGISTERED).count()


def delete_course_class(course_class):
    db.session.delete(course_class)
    db.session.commit()



def register_course(semester_id, student_id, course_class_id):
    reg = get_registration(student_id, course_class_id, semester_id)
    try:
        if reg is not None:
            reg.pre_status = reg.status
            reg.status = RegistrationStatus.REGISTERED
            reg.updated_at = datetime.now()
        else:
            reg = Registration(
                student_id=student_id,
                course_class_id=course_class_id,
                semester_id=semester_id,
                pre_status=RegistrationStatus.REGISTERED,
                status=RegistrationStatus.REGISTERED,
                created_date=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(reg)

        db.session.commit()
        return reg

    except Exception:
        db.session.rollback()
        raise

def get_next_semester():
    now = date.today()

    return Semester.query.filter(
        Semester.start_registration_date > now
    ).order_by(
        Semester.start_registration_date.asc()
    ).first()


def get_review_registration_semester():
    now = date.today()

    return Semester.query.filter(
        Semester.start_registration_date <= now + timedelta(days=1),
        Semester.end_registration_date >= now
    ).order_by(
        Semester.start_registration_date.asc()
    ).first()

def get_recent_past_semester():
    now = date.today()

    return Semester.query.filter(
        Semester.end_date < now
    ).order_by(Semester.end_date.desc()).first()


def get_courses_by_ids(ids):
    if not ids:
        return []
    return db.session.query(Course).filter(Course.id.in_(ids)).all()

def get_next_course_class_name(course_id, semester_id):
    course = db.session.get(Course, course_id)
    semester = get_semester_by_id(semester_id)

    max_index = (db.session.query(func.max(CourseClass.class_index))
                 .filter(
                     CourseClass.course_id == course_id,
                     CourseClass.semester_id == semester_id
                 )
                 .scalar())

    next_index = (max_index or 0) + 1

    name = f"{course.course_code}-{semester.name}-L{next_index:02d}"

    return name, next_index

def count_registered_students(course_class_id):
    return db.session.query(Registration).filter(
        Registration.course_class_id == course_class_id
    ).count()