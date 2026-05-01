from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum as SQLEnum, DateTime, func, Double
from sqlalchemy.orm import relationship, validates
from enum import Enum
from course import db, app


class ConfigEnum(Enum):
    MAX_CREDITS = "MAX_CREDITS"
    MIN_CREDITS = "MIN_CREDITS"
    MAX_STUDENTS_PER_CLASS = "MAX_STUDENTS_PER_CLASS"
    CANCEL_DEADLINE_DAYS = "CANCEL_DEADLINE_DAYS"

class UserRole(Enum):
    USER = (1, "Sinh viên")
    ADMIN = (2, "Quản trị viên")

    def __init__(self, id, label):
        self.id = id
        self.label = label

class Day(Enum):
    MONDAY = ("MON", "Thứ 2")
    TUESDAY = ("TUE", "Thứ 3")
    WEDNESDAY = ("WED", "Thứ 4")
    THURSDAY = ("THU", "Thứ 5")
    FRIDAY = ("FRI", "Thứ 6")
    SATURDAY = ("SAT", "Thứ 7")
    SUNDAY = ("SUN", "Chủ nhật")

    def __init__(self, value, label):
        self._value_ = value
        self.label = label

class Session(Enum):
    MORNING   = ("Sáng",     "07:30", "12:00")
    AFTERNOON = ("Chiều",    "13:00", "17:30")
    EVENING   = ("Tối",      "18:00", "21:30")

    def __init__(self, label: str, start: str, end: str):
        self.label = label
        self.start_time = start
        self.end_time = end

    def __str__(self):
        return f"{self.label} ({self.start_time} - {self.end_time})"

    @property
    def display(self):
        return f"{self.label}<br><small class='text-muted'>({self.start_time} - {self.end_time})</small>"

class RegistrationStatus(Enum):
    REGISTERED = "REGISTERED"
    STUDENT_CANCELLED = "STUDENT_CANCELLED"
    SYSTEM_CANCELLED = "SYSTEM_CANCELLED"





class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=func.now())
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


class CourseClassScheduleRoom(Base):
    __tablename__ = "class_schedules"

    course_class_id = Column(ForeignKey("course_classes.id"))
    slot_id = Column(ForeignKey("schedule_slots.id"))
    room_id = Column(ForeignKey("rooms.id"))
    semester_id = Column(ForeignKey("semesters.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('course_class_id', 'slot_id'),
        db.UniqueConstraint('slot_id', 'room_id','semester_id')
    )
    course_class = relationship("CourseClass", back_populates="schedule_associations")
    slot = relationship("ScheduleSlot", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")
    semester = relationship("Semester", backref="class_schedules")



class CourseClass(Base):
    __tablename__ = "course_classes"

    id = Column(Integer, primary_key=True)
    class_code = Column(String(255))
    course_id = Column(Integer, ForeignKey("courses.id"))
    max_students = Column(Integer)
    is_midterm_tested = Column(Boolean, default=False)
    class_index = db.Column(db.Integer, nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)

    schedule_associations = relationship(
        "CourseClassScheduleRoom",
        back_populates="course_class",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint('course_id', 'semester_id', 'class_index'),
    )

    registrations = db.relationship("Registration", backref="course_class")
    semester = db.relationship("Semester", backref="course_classes")

    @property
    def current_size(self):
        return db.session.query(func.count(Registration.id)).filter(
            Registration.course_class_id == self.id,
            Registration.status == RegistrationStatus.REGISTERED
        ).scalar()

    @validates('max_students')
    def validate_max_students(self, key, value):
        if value <= 0:
            raise ValueError("Sĩ số phải lớn hơn 0")
        return value

class ScheduleSlot(Base): #ca học
    __tablename__ = "schedule_slots"

    weekday = Column(SQLEnum(Day), nullable=False)
    session = Column(SQLEnum(Session), nullable=False)

    schedules = relationship(
        "CourseClassScheduleRoom",
        back_populates="slot",
        cascade="all, delete-orphan"
    )
    __table_args__ = (
        db.UniqueConstraint('weekday', 'session', name='unique_slot'),
    )

class Room(Base):
    __tablename__ = "rooms"

    name = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)

    schedules = relationship(
        "CourseClassScheduleRoom",
        back_populates="room",
        cascade="all, delete-orphan"
    )

class Semester(Base):
    __tablename__ = "semesters"

    name = Column(String(50))
    year = Column(Integer)
    start_date = Column(db.Date)
    end_date = Column(db.Date)
    is_auto_cancelled = Column(db.Boolean, default=False)
    start_registration_date = Column(db.Date)
    end_registration_date = Column(db.Date)

    registrations = relationship("Registration", backref="semester")


class Registration(Base):
    __tablename__ = "registrations"

    student_id = Column(Integer, ForeignKey("students.id"))
    course_class_id = Column(Integer, ForeignKey("course_classes.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    updated_at = Column(DateTime)
    pre_status = Column(SQLEnum(RegistrationStatus), default=RegistrationStatus.REGISTERED)
    status = Column(SQLEnum(RegistrationStatus), default=RegistrationStatus.REGISTERED)

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