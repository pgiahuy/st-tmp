from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from course import db, app


class UserRole(Enum):
    USER = 1
    ADMIN = 2

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    def __str__(self):
        return getattr(self, "name", str(self.id))


class User(Base):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)

    student = relationship("Student", backref="user", uselist=False)


class Student(Base):
    __tablename__ = "students"

    user_id = Column(Integer, ForeignKey("users.id"))
    mssv = Column(String(10), unique=True, nullable=False)
    full_name = Column(String(200))
    email = Column(String(200), unique=True)

    registrations = relationship("Registration", backref="student")


class Course(Base):
    __tablename__ = "courses"

    course_code = Column(String(20), unique=True, nullable=False)
    course_name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)

    classes = relationship("Class", backref="course")

    prerequisites = relationship(
        "Course",
        secondary="course_prerequisites",
        primaryjoin="Course.id==CoursePrerequisite.course_id",
        secondaryjoin="Course.id==CoursePrerequisite.prerequisite_id",
        backref="required_for"
    )

class Class(Base):
    __tablename__ = "classes"

    class_code = Column(String(20), unique=True)
    course_id = Column(Integer, ForeignKey("courses.id"))

    schedule = Column(String(50))  # Mon-1-3 / Tue-1-5 / Sat-7-11
    room_id = Column(Integer, ForeignKey("rooms.id"))
    room = db.relationship("Room", backref="classes")
    max_students = Column(Integer)
    registrations = db.relationship("Registration", backref="clazz")

class Room(Base):
    __tablename__ = "rooms"

    name = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)

class Semester(Base):
    __tablename__ = "semesters"

    name = Column(String(50))
    year = Column(Integer)
    start_date = Column(db.Date)
    registration_deadline = Column(db.Date)

    registrations = relationship("Registration", backref="semester")


class Registration(Base):
    __tablename__ = "registrations"

    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))

    registered_at = Column(DateTime, default=datetime.now())

    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', name='unique_registration'),
    )


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    course_id = Column(Integer, ForeignKey("courses.id"))
    prerequisite_id = Column(Integer, ForeignKey("courses.id"))

class Rule(Base):
    __tablename__ = "rules"

    key = Column(String(50), unique=True, nullable=False)
    value = Column(String(50), nullable=False)
    description = Column(String(255))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()