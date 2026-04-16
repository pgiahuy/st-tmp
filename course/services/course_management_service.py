from course import dao
from course.exceptions import BusinessException
from course.models import CourseClassSchedule, ConfigEnum


def delete_course_class_service(session, course_class_id):
    count = dao.count_course_registrations(session, course_class_id)

    if count > 0:
        raise BusinessException(f"Không thể xoá vì đã có {count} sinh viên đăng ký")

    course_class = dao.get_course_class_by_id(course_class_id)

    if not course_class:
        raise ValueError("Class not found")

    dao.delete_course_class(session, course_class)
    return True


def validate_course_class(semester_id, room_id , slot_ids, max_students, course_class_id=None):

    room = dao.get_room__by_id(room_id)
    if not room:
        raise ValueError("Room not found")

    validate_max_students(room, max_students)

    conflict = validate_schedule_conflict(
        semester_id, room, slot_ids, course_class_id
    )

    return conflict


def validate_max_students(room, max_students):
    max_limit = dao.get_config_value(ConfigEnum.MAX_STUDENTS_PER_CLASS, 50)

    limit = min(max_limit, room.capacity)

    if max_students > limit:
        raise BusinessException(
            f"Số sinh viên tối đa là {limit} (do giới hạn lớp và phòng)"
        )

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

def build_schedule_associations(course_class, slots):
    return [
        CourseClassSchedule(course_class=course_class, slot=s)
        for s in slots
    ]