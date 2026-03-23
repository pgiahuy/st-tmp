import hashlib

from sqlalchemy.exc import IntegrityError

from course import db, app
from course.models import User, Student, Course, Room, Rule


def hash_password(password):
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()

def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password, session):
    if not username or username is None:
        raise Exception("Vui lòng nhập tên đăng nhập!")
    if not password or password is None:
        raise Exception("Vui lòng nhập mật khẩu!")

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return session.query(User).filter_by(username=username, password=password).first()




def add_user_student(student_id = None, password = None):

    student = db.session.query(Student).filter_by(id=student_id).first()
    if not student:
        raise Exception("Sinh viên không tồn tại!")

    if not password:
        password = app.config.get("DEFAULT_PASSWORD")

    user = User(username=student.mssv, password=hash_password(password), student=student)
    db.session.add(user)
    return user


def add_student(mssv,full_name, email):
    student = Student(mssv=mssv, full_name=full_name, email=email)
    db.session.add(student)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Sinh viên đã tồn tại!')

def add_course(course_code, course_name, credits):
    course = Course(course_code=course_code, course_name=course_name, credits=credits)
    db.session.add(course)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

def add_room(name, capacity):
    room = Room(name=name, capacity=capacity)
    db.session.add(room)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def add_rule(key, value,name,description=None):
    rule = Rule(key=key, value=value,name=name, description=description)
    db.session.add(rule)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

def change_password(user_id, old_password, new_password):
    user = get_user_by_id(user_id)

    if not user:
        return {"error": "User không tồn tại"}

    # check mật khẩu cũ
    if user.password != hash_password(old_password):
        return {"error": "Mật khẩu cũ không đúng"}

    # update mật khẩu mới
    user.password = hash_password(new_password)
    db.session.commit()

    return {"success": True}