from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum as SQLEnum, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from course import db, app


class UserRole(Enum):
    USER = (1, "Sinh viên")
    ADMIN = (2, "Quản trị viên")

    def __init__(self, id, label):
        self.id = id
        self.label = label

class Day(Enum):
    MONDAY = "Mon"
    TUESDAY = "Tue"
    WEDNESDAY = "Wed"
    THURSDAY = "Thu"
    FRIDAY = "Fri"
    SATURDAY = "Sat"
    SUNDAY = "Sun"

class Session(Enum):
    MORNING   = ("Sáng",     "07:30", "12:00")
    AFTERNOON = ("Chiều",    "13:00", "17:30")
    EVENING   = ("Tối",      "18:00", "21:30")

    def __init__(self, label: str, start: str, end: str):
        self.label = label
        self.start_time = start
        self.end_time = end

    def __str__(self):
        return self.label

    @property
    def display(self):
        return f"{self.label}<br><small class='text-muted'>({self.start_time} - {self.end_time})</small>"



class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    def __str__(self):
        return getattr(self, "name", str(self.id))



class User(Base, UserMixin):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)

    student = relationship("Student", backref="user", uselist=False)

    @property
    def is_active(self):
        return self.active



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

    classes = relationship("CourseClass", backref="course")

    prerequisites = relationship(
        "Course",
        secondary="course_prerequisites",
        primaryjoin="Course.id==CoursePrerequisite.course_id",
        secondaryjoin="Course.id==CoursePrerequisite.prerequisite_id",
        backref="required_for"
    )


class CourseClassSchedule(Base):
    __tablename__ = "course_class_schedule_assoc"
    id = None

    course_class_id = Column(Integer, ForeignKey("course_classes.id"), primary_key=True)
    slot_id = Column(Integer, ForeignKey("schedule_slots.id"), primary_key=True)

    course_class = relationship("CourseClass", back_populates="schedule_associations")
    slot = relationship("ScheduleSlot", back_populates="class_associations")


class CourseClass(Base):
    __tablename__ = "course_classes"

    id = Column(Integer, primary_key=True)
    class_code = Column(String(20), unique=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    max_students = Column(Integer)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)

    schedule_associations = relationship(
        "CourseClassSchedule",
        back_populates="course_class",
        cascade="all, delete-orphan"
    )

    room = db.relationship("Room", backref="classes")
    registrations = db.relationship("Registration", backref="course_class")
    semester = db.relationship("Semester", backref="course_classes")

    @property
    def current_size(self):
        return len(self.registrations)

class ScheduleSlot(Base): #ca học
    __tablename__ = "schedule_slots"

    id = Column(Integer, primary_key=True)
    weekday = Column(SQLEnum(Day), nullable=False)
    session = Column(SQLEnum(Session), nullable=False)

    class_associations = relationship("CourseClassSchedule", back_populates="slot")


class Room(Base):
    __tablename__ = "rooms"
    name = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)



class Semester(Base):
    __tablename__ = "semesters"

    name = Column(String(50))
    year = Column(Integer)
    start_date = Column(db.Date)
    end_date = Column(db.Date)

    start_registration_date = Column(db.Date)
    end_registration_date = Column(db.Date)

    registrations = relationship("Registration", backref="semester")


class Registration(Base):
    __tablename__ = "registrations"

    student_id = Column(Integer, ForeignKey("students.id"))
    course_class_id = Column(Integer, ForeignKey("course_classes.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))

    registered_at = Column(DateTime, default=func.now())

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_class_id', name='unique_registration'),
    )


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    course_id = Column(Integer, ForeignKey("courses.id"))
    prerequisite_id = Column(Integer, ForeignKey("courses.id"))



class SystemConfig(Base):
    __tablename__ = "system_configs"

    key = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    value = Column(String(50), nullable=False)
    description = Column(String(255))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()