from datetime import datetime, timedelta

from course import db, dao
from course.exceptions import BusinessException
from course.models import ConfigEnum


def register_course(semester_id , student_id, course_class_id):

    student = dao.get_student_by_id(student_id)
    course_class = dao.get_course_class_by_id(course_class_id)

    if not course_class or not student:
        raise ValueError("Không tìm thấy dữ liệu sinh viên hoặc lớp học.")

    if dao.course_class_is_full(course_class_id):
        raise BusinessException(f"Lớp {course_class.class_code} đã đầy!")

    conflicting_class = dao.get_conflicting_class(student_id, course_class_id, semester_id)
    if conflicting_class:
        raise BusinessException(f"Trùng lịch với lớp {conflicting_class.class_code}")

    if dao.check_duplicate_in_semester(semester_id ,student_id, course_class_id):
        raise BusinessException("Bạn đã đăng ký một lớp khác của môn học này trong học kỳ này rồi!")

    if not dao.check_not_yet_studied(semester_id , student_id, course_class_id):
        raise BusinessException("Bạn đã hoàn thành môn học này ở các học kỳ trước!")

    semester = dao.get_semester_by_id(semester_id)
    if not semester:
        raise BusinessException("Không tìm thấy học kỳ")

    now = datetime.now().date()
    if semester.start_registration_date and now < semester.start_registration_date :
        raise BusinessException("Không được đăng ký trước thời gian đăng ký môn!")
    if semester.end_registration_date and now > semester.end_registration_date:
        raise BusinessException("Không được đăng ký sau thời gian đăng ký môn!")



    if not dao.check_studied_prerequisites( semester_id ,student_id, course_class_id):
        raise BusinessException("Chưa hoàn thành môn tiên quyết!")

    max_credits_limit = dao.get_config_value(ConfigEnum.MAX_CREDITS, 25)

    current_credits = dao.get_total_credits(student_id, semester_id)
    new_credits = course_class.course.credits

    if current_credits + new_credits > max_credits_limit:
        raise BusinessException(f"Vượt quá giới hạn {max_credits_limit} tín chỉ/học kỳ!")

    if not course_class.active:
        raise ValueError("Lớp hiện không mở!")
    dao.register_course(semester_id, student_id, course_class_id)

    return True


def confirm_registration(semester_id, student_id):
    min_credits_limit = dao.get_config_value(ConfigEnum.MIN_CREDITS, 12)

    total = dao.get_total_credits(student_id,semester_id)

    if total < min_credits_limit:
        raise BusinessException(f"Bạn cần đăng ký tối thiểu {min_credits_limit} tín chỉ để xuất phiếu. (Hiện có: {total})")

    return True



def cancel_registration(semester_id, student_id, course_class_id):

    reg = dao.get_registration(student_id, course_class_id, semester_id)

    if not reg:
        raise BusinessException("Sinh viên chưa đăng ký lớp này")

    now = datetime.now().date()


    if reg.semester.start_date and now > reg.semester.start_date + timedelta(days=14):
        raise BusinessException("Không được huỷ môn sau 2 tuần bắt đầu học kỳ!")

    if reg.is_midterm_tested is True:
        raise BusinessException("Không được huỷ sau khi đã thi giữa kỳ")

    dao.student_cancel_registration(reg)
    return True