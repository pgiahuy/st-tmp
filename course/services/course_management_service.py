from course import dao
from course.models import CourseClassSchedule


def delete_course_class_service(session, course_class_id):
    count = dao.count_course_registrations(session, course_class_id)

    if count > 0:
        raise ValueError(f"Không thể xoá vì đã có {count} sinh viên đăng ký")

    course_class = dao.get_course_class_by_id(course_class_id)

    if not course_class:
        raise ValueError("Class not found")

    dao.delete_course_class(session, course_class)
    return True

def validate_schedule_conflict(session, room, slot_ids, class_id=None):
    conflict = dao.check_schedule_conflict(
        session,
        room.id,
        slot_ids,
        class_id
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