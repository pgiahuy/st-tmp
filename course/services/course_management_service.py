from datetime import date

from course import dao
from course.exceptions import BusinessException, PermissionDeniedException
from course.models import CourseClassSchedule, ConfigEnum, UserRole


def handle_course_class_change_service(user_role,semester_id, room_id, slot_ids, max_students,
                                       selected_slots_objects, model, class_id=None):
    print("TYPEEEEE maxs_students=======")
    print(type(max_students), max_students)


    if user_role != UserRole.ADMIN:
        raise PermissionDeniedException()


    result = validate_course_class(
        semester_id,
        room_id,
        slot_ids,
        max_students,
        class_id
    )

    if result:
        conflict = result["conflict"]
        slot = result["slot"]
        time_info = f"{slot.weekday.label} ({slot.session})" \
            if slot else "Không xác định"

        raise BusinessException(
            f"Trùng lịch: Phòng đã được sử dụng bởi lớp '{conflict.class_code}' vào {time_info}"
        )

    return [
            CourseClassSchedule(course_class=model, slot=s)
            for s in selected_slots_objects
        ]



def delete_course_class_service(user_role,course_class_id):
    if user_role != UserRole.ADMIN:
        raise PermissionDeniedException()
    count = dao.count_course_registrations(course_class_id)

    if count > 0:
        raise BusinessException(f"Không thể xoá vì đã có {count} sinh viên đăng ký")

    course_class = dao.get_course_class_by_id(course_class_id)

    if not course_class:
        raise ValueError("Class not found")

    dao.delete_course_class(course_class)
    return True




# main check
def validate_course_class(semester_id, room_id , slot_ids, max_students, course_class_id=None):
    print("TYPEEEEE maxs_students=======")
    print(type(max_students), max_students)

    semester = dao.get_semester_by_id(semester_id)
    today = date.today()

    if semester.end_date and today > semester.end_date:
        raise BusinessException("Không thể tạo lớp cho học kỳ đã kết thúc")


    room = dao.get_room_by_id(room_id)
    if not room:
        raise ValueError("Room not found")

    max_limit = dao.get_config_value(ConfigEnum.MAX_STUDENTS_PER_CLASS, 50)

    validate_max_students(room, max_students,max_limit)

    conflict = validate_schedule_conflict(
        semester_id, room, slot_ids, course_class_id
    )

    return conflict

# như tên:)
def validate_max_students(room, max_students, max_limit):
    limit = min(max_limit, room.capacity)

    if max_students > limit:
        raise BusinessException(
            f"Số sinh viên tối đa là {limit} (do giới hạn lớp và phòng)"
        )
    if max_students < 1:
        raise BusinessException(
            f"Số sinh viên tối thiểu là 1"
        )

# trùng lịch
def validate_schedule_conflict(semester_id,room, slot_ids, course_class_id):
    conflict = dao.check_schedule_conflict(
        semester_id,
        room.id,
        slot_ids,
        course_class_id
    )

    if not conflict:
        return None

    conflicting_slot = next(
        (a.slot for a in conflict.schedule_associations if a.slot.id in slot_ids),
        None
    )

    return {
        "conflict": conflict,
        "slot": conflicting_slot
    }

