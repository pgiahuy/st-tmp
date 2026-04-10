from sqlalchemy.exc import IntegrityError

from course import db, app
from course.dao import hash_password
from course.models import CourseClass, Student, User, Course, Room, SystemConfig, Semester


def add_course_class(class_code, course_id, room_id, max_students):
    c_class = CourseClass(
        class_code=class_code,
        course_id=course_id,
        room_id=room_id,
        max_students=max_students
    )
    db.session.add(c_class)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print(f"Lớp {class_code} đã tồn tại hoặc lỗi khóa ngoại!")

def add_student_with_user(mssv, full_name, email, password=None):
    try:
        student = Student(
            mssv=mssv,
            full_name=full_name,
            email=email
        )
        db.session.add(student)
        db.session.flush()

        if not password:
            password = app.config.get("DEFAULT_PASSWORD")

        user = User(
            username=student.mssv,
            password=hash_password(password),
            student=student
        )
        db.session.add(user)

        db.session.commit()

        return student

    except IntegrityError:
        db.session.rollback()
        raise Exception("Sinh viên hoặc user đã tồn tại!")


def add_course(course_code, course_name, credits):
    course = Course(course_code=course_code, course_name=course_name, credits=credits)
    db.session.add(course)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

def add_semester(name, year, start_date, end_date,
                 start_registration_date, end_registration_date):

    sem = Semester(
        name=name,
        year=year,
        start_date=start_date,
        end_date=end_date,
        start_registration_date=start_registration_date,
        end_registration_date=end_registration_date
    )

    db.session.add(sem)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Lỗi khi thêm semester!")

def add_room(name, capacity):
    room = Room(name=name, capacity=capacity)
    db.session.add(room)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def add_user(username, password):
    user = User(username=username, password=hash_password(password))
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def add_system_config(key, value,name,description=None):
    rule = SystemConfig(key=key, value=value,name=name, description=description)
    db.session.add(rule)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
