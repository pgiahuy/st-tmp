from datetime import date

from course import dao, db
from course.exceptions import BusinessException, PermissionDeniedException
from course.models import CourseClassScheduleRoom, ConfigEnum, UserRole, Course


def handle_course_class_change_service(user_role,semester_id, room_id, slot_ids, max_students,
                                       selected_slots_objects, model, course_id, class_id=None):
    print("TYPEEEEE maxs_students=======")
    print(type(max_students), max_students)

    if user_role != UserRole.ADMIN:
        raise PermissionDeniedException()



    current_count = (
        dao.count_registered_students(class_id)
        if class_id else 0
    )

    if max_students < current_count:
        raise BusinessException(
            f"Sĩ số không thể nhỏ hơn số sinh viên đã đăng ký ({current_count})"
        )
    print(f"course_id = {course_id}===")
    print(type(course_id), course_id)
    print("////////////////")
    print(model.semester_id)
    print("course_id=", course_id)
    print("semester_id=", semester_id)
    print("class_index", model.class_index)





    result = validate_course_class(
        semester_id,
        model.semester_id,
        room_id,
        slot_ids,
        max_students,
        class_id,
    )

    if result:
        conflict = result["conflict"]
        slot = result["slot"]
        time_info = f"{slot.weekday.label} ({slot.session})" \
            if slot else "Không xác định"

        raise BusinessException(
            f"Trùng lịch: Phòng đã được sử dụng bởi lớp '{conflict.course_class.class_code}' vào {time_info}"
        )

    existing = dao.find_course_class_by_unique_keys(
        course_id=course_id,
        semester_id=semester_id,
        class_index=model.class_index,
        exclude_id=class_id
    )

    if existing:
        raise BusinessException("Trùng lớp học phần")

    return [
        CourseClassScheduleRoom(
            course_class_id=model.id,
            slot_id=s.id,
            room_id=room_id,
            semester_id=semester_id
        )
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
def validate_course_class(semester_id,model_semester_id, room_id , slot_ids, max_students, course_class_id=None):
    print("TYPEEEEE maxs_students=======")
    print(type(max_students), max_students)
    room = dao.get_room_by_id(room_id)
    if not room:
        raise ValueError("Room not found")

    model_semester = dao.get_semester_by_id(model_semester_id)
    new_semester = dao.get_semester_by_id(semester_id)
    today = date.today()

    if model_semester and model_semester.end_date and today > model_semester.end_date:
        raise BusinessException(f"Không thể thao tác vì lớp thuộc học kỳ {model_semester.name} - {model_semester.year}, đã kết thúc !")

    if new_semester.end_date and today > new_semester.end_date:
        raise BusinessException(f"Học kỳ {new_semester.name} - {new_semester.year} đã kết thúc !")

    room = dao.get_room_by_id(room_id)
    if not room:
        raise ValueError("Room not found")

    max_limit = dao.get_config_value(ConfigEnum.MAX_STUDENTS_PER_CLASS, 50)

    validate_max_students(room, max_students, max_limit)


    conflict = validate_schedule_conflict(
        semester_id, room_id, slot_ids, course_class_id
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
def validate_schedule_conflict(semester_id,room_id, slot_ids, course_class_id):
    conflict = dao.check_schedule_conflict(
        semester_id,
        room_id,
        slot_ids,
        course_class_id
    )

    if not conflict:
        return None

    conflicting_slot = conflict.slot if conflict.slot_id in slot_ids else None

    return {
        "conflict": conflict,
        "slot": conflicting_slot
    }

#check môn học chưa đc sử dụng
def check_unactive_course(course_id):
    return dao.check_unactive_course(course_id)


