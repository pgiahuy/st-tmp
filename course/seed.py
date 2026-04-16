# import json
# import os
# from datetime import datetime, date
# from sqlalchemy.exc import IntegrityError
#
# from course import app, db, dao, utils
# from course.dao import hash_password
# from course.models import User, Student, Course, CourseClass, ScheduleSlot, Room, Semester, Registration, CoursePrerequisite, SystemConfig, CourseClassSchedule, UserRole, Day, Session
#
#
#
# if __name__ == "__main__":
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#
#         # Load users
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'users.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for u in data['users']:
#             role = UserRole[u['role']]
#             utils.add_user(u['username'], u['password'])
#             user = User.query.filter_by(username=u['username']).first()
#             user.role = role
#             db.session.commit()
#
#         # Load students
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'students.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for s in data['students']:
#             utils.add_student_with_user(s['mssv'], s['full_name'],email=s['email'])
#
#         # Load courses
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'courses.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for c in data['courses']:
#             utils.add_course(**c)
#
#         # Load rooms
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'rooms.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for r in data['rooms']:
#             utils.add_room(**r)
#
#         # Load semesters
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'semesters.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for s in data['semesters']:
#             sem_data = s.copy()
#             sem_data['start_date'] = date.fromisoformat(s['start_date'])
#             sem_data['end_date'] = date.fromisoformat(s['end_date'])
#             sem_data['start_registration_date'] = date.fromisoformat(s['start_registration_date'])
#             sem_data['end_registration_date'] = date.fromisoformat(s['end_registration_date'])
#             utils.add_semester(**sem_data)
#
#         # Load schedule slots
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'schedule_slots.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for slot in data['slots']:
#             s = ScheduleSlot(
#                 weekday=Day[slot['weekday']],
#                 session=Session[slot['session']]
#             )
#             db.session.add(s)
#         db.session.commit()
#
#         # Load course classes
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'course_classes.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for cls in data['course_classes']:
#             c_class = CourseClass(
#                 class_code=cls['class_code'],
#                 course_id=cls['course_id'],
#                 room_id=cls['room_id'],
#                 max_students=cls['max_students'],
#                 semester_id=cls['semester_id']
#             )
#             db.session.add(c_class)
#         db.session.commit()
#
#         # Load class schedules
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'class_schedules.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for cs in data['class_schedules']:
#             assoc = CourseClassSchedule(
#                 course_class_id=cs['course_class_id'],
#                 slot_id=cs['slot_id']
#             )
#             db.session.add(assoc)
#         db.session.commit()
#
#         # Load prerequisites
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'prerequisites.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for pr in data['prerequisites']:
#             if 'course_id' in pr:
#                 p = CoursePrerequisite(
#                     course_id=pr['course_id'],
#                     prerequisite_id=pr['prerequisite_id']
#                 )
#                 db.session.add(p)
#         db.session.commit()
#
#
#
#         # Load rules
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'rules.json'), encoding='utf-8') as f:
#             data = json.load(f)
#         for rule in data['rules']:
#             utils.add_system_config(**rule)
#
