from course import db, dao
from course.dao import get_student_by_id, get_course_class_by_id, get_registration_semester, course_class_is_full, \
    get_conflicting_class, check_duplicate_in_semester, check_not_yet_studied, check_studied_prerequisites, \
    get_config_value, get_total_credits
from course.exceptions import BusinessException


def register_course(semester_id , student_id, course_class_id):

    student = get_student_by_id(student_id)
    course_class = get_course_class_by_id(course_class_id)

    if not course_class or not student:
        raise ValueError("Không tìm thấy dữ liệu sinh viên hoặc lớp học.")

    if course_class_is_full(course_class_id):
        raise BusinessException(f"Lớp {course_class.class_code} đã đầy!")

    conflicting_class = get_conflicting_class(student_id, course_class_id, semester_id)
    if conflicting_class:
        raise BusinessException(f"Trùng lịch với lớp {conflicting_class.class_code}")

    if check_duplicate_in_semester(semester_id ,student_id, course_class_id):
        raise BusinessException("Bạn đã đăng ký một lớp khác của môn học này trong học kỳ này rồi!")

    if not check_not_yet_studied(semester_id , student_id, course_class_id):
        raise BusinessException("Bạn đã hoàn thành môn học này ở các học kỳ trước!")

    if not check_studied_prerequisites( semester_id ,student_id, course_class_id):
        raise BusinessException("Chưa hoàn thành môn tiên quyết!")

    max_credits_limit = get_config_value('MAX_CREDITS', 25)

    current_credits = get_total_credits(student_id, semester_id)
    new_credits = course_class.course.credits

    if current_credits + new_credits > max_credits_limit:
        raise BusinessException(f"Vượt quá giới hạn {max_credits_limit} tín chỉ/học kỳ!")


    dao.register_course(semester_id, student_id, course_class_id)

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
