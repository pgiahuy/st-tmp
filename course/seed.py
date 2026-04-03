import json

import course.utils
from course import db, app, dao, utils
from course.models import User, Student, UserRole

# users > students > courses > prerequisites > semesters > rooms > classes > registrations

#
#
# with open('data/students.json', encoding='utf-8') as f:
#     with app.app_context():
#         data = json.load(f)
#         for s in data["students"]:
#             utils.add_student(
#                 mssv=s["mssv"],
#                 full_name=s["full_name"],
#                 email=s["email"]
#             )
#             utils.add_user(
#                 username=s["mssv"],
#                 password="Abc1234@",
#             )
#         db.session.commit()

# #
# with open('data/classes.json', encoding='utf-8') as f:
#     with app.app_context():
#         data = json.load(f)
#         for c in data["classes"]:
#             utils.add_course_class(
#                 class_code=c["class_code"],
#                 course_id=c["course_id"],
#                 room_id=c["room_id"],
#                 max_students=c["max_students"]
#             )
#         try:
#             db.session.commit()
#             print("Đã nạp thành công 50 lớp học!")
#         except Exception as e:
#             db.session.rollback()
#             print(f"Lỗi khi nạp lớp học: {e}")

# with open('data/rooms.json', encoding='utf-8') as f:
#     with app.app_context():
#         data = json.load(f)
#         for r in data["rooms"]:
#             utils.add_room(name=r["name"], capacity=r["capacity"])
#         db.session.commit()
#
with open('data/semesters.json', encoding='utf-8') as f:
    with app.app_context():
        data = json.load(f)
        for s in data["semesters"]:
            utils.add_semester(name=s["name"],
                           year=s["year"],
                           start_date=s["start_date"],
                           registration_deadline=s["registration_deadline"])
        db.session.commit()
#

#
# with open('data/rules.json', encoding='utf-8') as f:
#     with app.app_context():
#         data = json.load(f)
#         for r in data["rules"]:
#             utils.add_system_config(key=r["key"], value=r["value"], name=r["name"])
#         db.session.commit()
#
# with open('data/courses.json', encoding='utf-8') as f:
#     with app.app_context():
#         data = json.load(f)
#         for c in data["courses"]:
#             utils.add_course(course_code=c["course_code"],
#                            course_name=c["course_name"],
#                            credits=c["credits"])
#         db.session.commit()
#
