import json
from course import db, app, dao, utils
from course.models import User, UserRole

DATA_FILES = [
    {'file': 'data/rooms.json', 'func': utils.add_room},
    {'file': 'data/rules.json', 'func': utils.add_system_config},
    {'file': 'data/semesters.json', 'func': utils.add_semester},
    {'file': 'data/courses.json', 'func': utils.add_course},
    {'file': 'data/students.json', 'func': dao.add_student},
    {'file': 'data/classes.json', 'func': utils.add_course_class},
]


def load_data_from_json(file_path, add_func):
    try:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
            list_key = list(data.keys())[0]
            for item in data[list_key]:
                add_func(**item)
            db.session.commit()

    except Exception as e:
        print(e)


def create_default_users():

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=dao.hash_password("123"),
            role=UserRole.ADMIN
        )
        db.session.add(admin)


    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()


if __name__ == "__main__":
    with app.app_context():
        for config in DATA_FILES:
            load_data_from_json(config['file'], config['func'])

        create_default_users()
