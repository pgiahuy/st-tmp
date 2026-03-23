import json
from course import db, app, dao
from course.models import User, Student

# users > students > courses > prerequisites > semesters > rooms > classes > registrations

# with open('data/users.json', encoding='utf-8') as f:
#     with app.app_context():
#         data = json.load(f)
#         for u in data["users"]:
#             dao.add_user(student_id=u["student_id"], password=u["password"])
#         db.session.commit()

with open('data/rooms.json', encoding='utf-8') as f:
    with app.app_context():
        data = json.load(f)
        for r in data["rooms"]:
            dao.add_room(name=r["name"], capacity=r["capacity"])
        db.session.commit()


with open('data/rules.json', encoding='utf-8') as f:
    with app.app_context():
        data = json.load(f)
        for r in data["rules"]:
            dao.add_rule(key=r["key"], value=r["value"], name=r["name"])
        db.session.commit()

with open('data/courses.json', encoding='utf-8') as f:
    with app.app_context():
        data = json.load(f)
        for c in data["courses"]:
            dao.add_course(course_code=c["course_code"],
                           course_name=c["course_name"],
                           credits=c["credits"])
        db.session.commit()

with open('data/students.json', encoding='utf-8') as f:
    with app.app_context():
        data = json.load(f)
        for s in data["students"]:
            dao.add_student(
                mssv=s["mssv"],
                full_name=s["full_name"],
                email=s["email"]
            )
        db.session.commit()
# Tạo tạm tk admin
# from course.models import User, UserRole
#
# with app.app_context():
#     admin = User.query.filter_by(username="admin").first()
#
#     if not admin:
#         admin = User(
#             username="admin",
#             password=dao.hash_password("123456"),
#             role=UserRole.ADMIN
#         )
#         db.session.add(admin)
#         db.session.commit()