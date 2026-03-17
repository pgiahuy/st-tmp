import json
from course import db, app, dao
from course.models import User, Student

with open('data/users.json', encoding='utf-8') as f:
    with app.app_context():
        data = json.load(f)
        for u in data["users"]:
            dao.add_user(student_id=u["student_id"], password=u["password"])
        db.session.commit()

# with open('data/students.json', encoding='utf-8') as f:
#     with app.app_context():
#         data = json.load(f)
#         for s in data["students"]:
#             dao.add_student(
#                 mssv=s["mssv"],
#                 full_name=s["full_name"],
#                 email=s["email"]
#             )
#         db.session.commit()