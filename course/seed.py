# import json
# from course import db, app, dao, utils
# from course.models import User, UserRole
#
# DATA_FILES = [
#     {'file': 'data/rooms.json', 'func': utils.add_room},
#     {'file': 'data/rules.json', 'func': utils.add_system_config},
#     {'file': 'data/semesters.json', 'func': utils.add_semester},
#     {'file': 'data/courses.json', 'func': utils.add_course},
#     {'file': 'data/students.json', 'func': dao.add_student},
#     {'file': 'data/classes.json', 'func': utils.add_course_class},
# ]
#
#
# def load_data_from_json(file_path, add_func):
#     try:
#         with open(file_path, encoding='utf-8') as f:
#             data = json.load(f)
#             list_key = list(data.keys())[0]
#             for item in data[list_key]:
#                 add_func(**item)
#             db.session.commit()
#
#     except Exception as e:
#         print(e)
#
#
# def create_default_users():
#
#     if not User.query.filter_by(username="admin").first():
#         admin = User(
#             username="admin",
#             password=dao.hash_password("123"),
#             role=UserRole.ADMIN
#         )
#         db.session.add(admin)
#
#
#     try:
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#
#
# if __name__ == "__main__":
#     with app.app_context():
#         for config in DATA_FILES:
#             load_data_from_json(config['file'], config['func'])
#
#         create_default_users()
import json
import os
from datetime import datetime
from course import app, db
from models import Room, Semester, Course, Student, CourseClass, ScheduleSlot, CourseClassSchedule, User, UserRole
from werkzeug.security import generate_password_hash

import json
import os
import hashlib
from datetime import datetime
from course import app, db
# Đảm bảo import đầy đủ các Model
from models import (Room, Semester, Course, Student, CourseClass,
                    ScheduleSlot, CourseClassSchedule, User, UserRole, SystemConfig)


def load_json(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'data', filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def str_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def hash_pass(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def seed_data():
    with app.app_context():
        print("--- Đang dọn dẹp và khởi tạo Database mới...")
        db.drop_all()
        db.create_all()

        # 1. Nạp Quy định hệ thống (System Config)
        print("-> Đang nạp cấu hình hệ thống...")
        rules_data = load_json('rules.json')
        for rule in rules_data['rules']:
            db.session.add(SystemConfig(
                key=rule['key'],
                name=rule['name'],
                value=rule['value'],
                description=rule.get('description', '')
            ))

        # 2. Nạp Học kỳ (Semesters)
        print("-> Đang nạp danh sách học kỳ...")
        for s in load_json('semesters.json')['semesters']:
            db.session.add(Semester(
                name=s['name'],
                year=s['year'],
                start_date=str_to_date(s['start_date']),
                start_registration_date=str_to_date(s['start_registration_date']),
                registration_deadline=str_to_date(s['registration_deadline'])
            ))

        # 3. Nạp Phòng học & Môn học
        print("-> Đang nạp phòng học và môn học...")
        for r in load_json('rooms.json')['rooms']:
            db.session.add(Room(name=r['name'], capacity=r['capacity']))
        for c in load_json('courses.json')['courses']:
            db.session.add(Course(course_code=c['course_code'], course_name=c['course_name'], credits=c['credits']))

        # 4. Nạp Sinh viên
        print("-> Đang nạp danh sách sinh viên...")
        for st in load_json('students.json')['students']:
            db.session.add(Student(mssv=st['mssv'], full_name=st['full_name'], email=st.get('email')))

        db.session.commit()  # Commit đợt 1 để có ID cho các bảng quan hệ

        # 5. Nạp Lớp học phần
        print("-> Đang nạp lớp học phần...")
        for cl in load_json('classes.json')['classes']:
            db.session.add(CourseClass(
                class_code=cl['class_code'],
                course_id=cl['course_id'],
                room_id=cl['room_id'],
                max_students=cl['max_students'],
                semester_id=cl.get('semester_id', 1)
            ))

        # 6. Nạp Ca học (Slots)
        print("-> Đang nạp các ca học...")
        for sl in load_json('schedule_slots.json')['slots']:
            db.session.add(ScheduleSlot(weekday=sl['weekday'], session=sl['session']))

        db.session.commit()  # Commit đợt 2

        # 7. Nạp Chi tiết lịch học
        print("-> Đang xếp lịch học cho các lớp...")
        for sch in load_json('class_schedules.json')['class_schedules']:
            db.session.add(CourseClassSchedule(course_class_id=sch['course_class_id'], slot_id=sch['slot_id']))

        # 8. Tạo tài khoản User cho Sinh viên & Admin
        print("-> Đang khởi tạo tài khoản người dùng...")
        # Tạo Admin
        admin_user = User(
            username="admin",
            password=hash_pass("123"),
            role=UserRole.ADMIN,
            active=True
        )
        db.session.add(admin_user)

        # Tạo User cho từng sinh viên
        for s in Student.query.all():
            u = User(
                username=s.mssv,
                password=hash_pass("123"),
                role=UserRole.USER,
                active=True
            )
            u.student = s
            db.session.add(u)

        db.session.commit()
        print("\n--- DATABASE ĐÃ SẴN SÀNG ---")


if __name__ == "__main__":
    seed_data()