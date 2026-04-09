import hashlib
from datetime import datetime
# from zipimport import END_CENTRAL_DIR_SIZE

from cloudinary.provisioning import Role

from course import db,app
from course.models import User, Student, CourseClass, Registration, Semester, Course, CoursePrerequisite, UserRole, \
    CourseClassSchedule, SystemConfig
from sqlalchemy.exc import IntegrityError


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
    # 1. Xác định học kỳ
    semester = get_registration_semester()
    if not semester:
        print("--- DEBUG: KHONG TIM THAY HOC KY DANG KY ---")
        return []

    print(f"--- DEBUG: Dang check lop cho Hoc ky ID = {semester.id} ---")

    try:
        # 2. Xây dựng Query
        query = CourseClass.query.filter(
            CourseClass.semester_id == semester.id,
            CourseClass.active == True
        )

        if course_id:
            query = query.filter(CourseClass.course_id == course_id)

        if kw:
            query = query.join(Course).filter(Course.course_name.contains(kw))

        # 3. Thực thi query
        results = query.all()

        # In ra số lượng lớp tìm thấy
        print(f"--- DEBUG: Tim thay {len(results)} lop hoc phan ---")

        return results

    except Exception as e:
        # Nếu có lỗi (sai tên cột, sai bảng...), nó sẽ in ra đây
        print(f"--- LOI LOGIC: {str(e)} ---")
        return []


# def auth_user(username, password,role, session):
#     if not username or username is None:
#         raise Exception("Vui lòng nhập tên đăng nhập!")
#     if not password or password is None:
#         raise Exception("Vui lòng nhập mật khẩu!")
#     password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
#     return session.query(User).filter_by(username=username, password=password).first()

import hashlib
import re
from sqlalchemy import func

# hàm băm mật khẩu
def hash_password(password):
    if not password:
        return None
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()

# hàm validate chung để kt ở index.py và dao.py
def validate_auth(username, password, role):
    if not username or not username.strip():
        raise Exception("Vui lòng nhập tên đăng nhập!")
    if not password or not password.strip():
        raise Exception("Vui lòng nhập mật khẩu!")
    if not role:
        raise Exception("Vui lòng chọn vai trò!")

    if role == "USER":
        if not re.fullmatch(r"\d{10}", username.strip()):
            raise Exception("Mã số sinh viên phải là 10 chữ số!")


def auth_user(username, password, role, session):
    validate_auth(username, password, role)

    user = session.query(User).filter(
        func.lower(User.username) == username.lower(),
        User.password == hash_password(password)
    ).first()

    if user and user.role.name != role:
        return None

    return user



def get_course_class_by_id(id):
    return CourseClass.query.filter_by(id=id).first()

def get_all_course_classes():
    return CourseClass.query.filter(CourseClass.active == True).all()

# lấy danh sách môn học đc mở trong hk này ( môn học phần lấy distinct)
def get_courses_by_current_reg_semester():
    semester = get_registration_semester()
    if not semester:
        return []

    courses = db.session.query(Course).join(CourseClass).filter(CourseClass.semester_id == semester.id).distinct().all()

    return courses
#
# def register_course(student_id, course_class_id):
#     student = get_student_by_id(student_id)
#     course_class = get_course_class_by_id(course_class_id)
#     if not course_class:
#         return {"success": False, "message": "Không tìm thấy lớp học phần"}, 400
#     if not student:
#         return {"success": False, "message": "Không tìm thấy sinh viên"}, 400
#
#     if course_class_is_full(course_class_id):
#         raise Exception("Lớp đã đầy!")
#
#     conflicting_class = get_conflicting_class(student_id, course_class_id)
#     if conflicting_class:
#         new_class = CourseClass.query.get(course_class_id)
#
#         raise Exception(
#             f"Trùng lịch! Lớp {new_class.class_code} trùng lịch với lớp "
#             f"{conflicting_class.class_code} ({conflicting_class.course.course_name}) "
#             f" đã đăng ký"
#         )
#
#     if not check_not_yet_studied(student_id, course_class_id):
#         raise Exception("Không được đăng ký môn đã học!")
#
#     if not check_studied_prerequisites(student_id, course_class_id):
#         raise Exception("Chưa học xong các môn tiên quyết!")
#
#     if check_duplicate_in_semester(student_id, course_class_id):
#         raise Exception("Không được đăng ký trùng môn!")
#     semester = get_registration_semester()
#
#
#     print("semester = ", semester.id)
#     reg = Registration(student_id=student_id, course_class_id=course_class_id,
#                        semester_id=semester.id)
#
#     db.session.add(reg)
#     db.session.commit()
#
#     return {"student_id": student_id, "class_id": course_class_id}

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

    # --- KIỂM TRA CÁC RÀNG BUỘC ---

    # 1. Kiểm tra sĩ số (Lấy từ lớp hoặc từ config mặc định nếu lớp không có)
    if course_class_is_full(course_class_id):
        raise Exception(f"Lớp {course_class.class_code} đã đầy!")

    ## 1. Kiểm tra trùng lịch (Check Slot)
    conflicting_class = get_conflicting_class(student_id, course_class_id, semester.id)
    if conflicting_class:
        raise Exception(f"Trùng lịch với lớp {conflicting_class.class_code}")

    # 2. Kiểm tra TRÙNG MÔN trong cùng học kỳ này
    # Nếu tick ID 1 rồi tick ID 2 của cùng 1 môn, nó phải báo lỗi này trước
    if check_duplicate_in_semester(student_id, course_class_id):
        raise Exception("Bạn đã đăng ký một lớp khác của môn học này trong học kỳ này rồi!")

    # 3. Kiểm tra ĐÃ HỌC XONG ở các học kỳ trước (Lịch sử)
    if not check_not_yet_studied(student_id, course_class_id):
        raise Exception("Bạn đã hoàn thành môn học này ở các học kỳ trước!")

    # 4. Kiểm tra môn tiên quyết
    if not check_studied_prerequisites(student_id, course_class_id):
        raise Exception("Chưa hoàn thành môn tiên quyết!")
    # 4. Kiểm tra giới hạn TÍN CHỈ TỐI ĐA (Lấy từ Database)
    max_credits_limit = get_config_value('MAX_CREDITS', 25)  # Mặc định 25 nếu DB trống

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

    # Lấy giới hạn tối thiểu từ Database
    min_credits_limit = get_config_value('MIN_CREDITS', 12)

    total = get_total_credits(student, semester.id)

    if total < min_credits_limit:
        raise Exception(f"Bạn cần đăng ký tối thiểu {min_credits_limit} tín chỉ để xuất phiếu. (Hiện có: {total})")

    return {"success": True, "message": "Xác nhận thành công!"}

def get_course_classes_for_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return []

    semester = get_current_semester()
    registered_classes = [
        reg.course_class
        for reg in student.registrations
        if reg.semester_id == semester.id
    ]

    return registered_classes

def get_current_semester():
    today = datetime.now()
    return Semester.query.filter(
        Semester.start_date <= today,
        # Semester.end_date >= today
    ).order_by(Semester.start_date.desc()).first()

def get_registration_semester():
    today = datetime.now().date()
    return Semester.query.filter(Semester.start_registration_date <= today, Semester.registration_deadline >= today).order_by(Semester.start_date.asc()).first()

def add_student(mssv,full_name, email):
    student = Student(mssv=mssv, full_name=full_name, email=email)
    db.session.add(student)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Sinh viên đã tồn tại!')

# def get_total_credits(student, semester):
#     total = 0
#     for reg in student.registrations:
#         if reg.semester_id == semester.id:
#             total += reg.class_section.course.credits
#     return total
#
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
    # Lấy học kỳ đang mở đăng ký hiện tại
    reg_semester = get_registration_semester()

    student_studied = []
    for reg in student.registrations:
        # CHỖ QUAN TRỌNG: Bỏ qua các môn của học kỳ đang đăng ký
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



# var ở đây
# def get_conflicting_class(student_id, course_class_id):
#
#     new_class = CourseClass.query.get(course_class_id)
#     current_semester = get_current_semester()
#
#     if not new_class or not current_semester:
#         return None
#
#     student = get_student_by_id(student_id)
#     registered_classes = [
#         reg.course_class for reg in student.registrations
#         if reg.semester_id == current_semester.id
#     ]
#
#     new_slots = {
#         (assoc.slot.weekday, assoc.slot.session)
#         for assoc in new_class.schedule_associations if assoc.slot
#     }
#
#     for old_class in registered_classes:
#         old_slots = {
#             (assoc.slot.weekday, assoc.slot.session)
#             for assoc in old_class.schedule_associations if assoc.slot
#         }
#
#         if new_slots.intersection(old_slots):
#             return old_class
#
#     return None


def get_conflicting_class(student_id, course_class_id, reg_semester_id):
    # 1. Lấy thông tin lớp mới và các slot lịch học của nó
    new_class = CourseClass.query.get(course_class_id)
    if not new_class or not reg_semester_id:
        return None

    # Tạo Set các cặp (Thứ, Ca) của lớp mới
    new_slots = {
        (assoc.slot.weekday, assoc.slot.session)
        for assoc in new_class.schedule_associations if assoc.slot
    }

    # 2. Truy vấn trực tiếp các lớp ĐÃ ĐĂNG KÝ trong học kỳ đang xét
    # Tối ưu: Lọc ngay tại tầng Database thay vì lọc bằng Python list comprehension
    registered_registrations = Registration.query.filter_by(
        student_id=student_id,
        semester_id=reg_semester_id
    ).all()

    for reg in registered_registrations:
        old_class = reg.course_class

        # Bỏ qua nếu là chính lớp đang xét (đề phòng trường hợp update)
        if old_class.id == course_class_id:
            continue

        # Lấy Set các cặp (Thứ, Ca) của lớp đã đăng ký
        old_slots = {
            (assoc.slot.weekday, assoc.slot.session)
            for assoc in old_class.schedule_associations if assoc.slot
        }

        # 3. Kiểm tra giao nhau (Conflict)
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

    conflict = db_session.query(CourseClassSchedule).join(CourseClass).filter(
        CourseClass.room_id == room_id,
        CourseClassSchedule.slot_id.in_(slot_ids)
    )
    if current_class_id:
        conflict = conflict.filter(CourseClass.id != current_class_id)

    return conflict.first()

