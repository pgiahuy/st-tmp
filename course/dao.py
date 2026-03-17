import hashlib

from sqlalchemy.exc import IntegrityError

from course import db
from course.models import User, Student, Course


def md5_hash(password):
    return hashlib.md5(password.strip().encode('utf-8')).hexdigest()

def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()

def add_user(student_id = None, password = None):

    student = db.session.query(Student).filter_by(id=student_id).first()
    user = User(username=student.mssv, password=md5_hash(password), student=student)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Username đã tồn tại!')


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

