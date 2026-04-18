
from course.models import Student
from course import db, dao

def auto_cancel_job():
    semester = dao.get_current_semester()
    print('current_semester:', semester)

    if not semester or semester.is_auto_cancelled:
        raise Exception("Học kỳ này đã quét danh sách!")

    semester_id = semester.id
    students = db.session.query(Student).all()
    for student in students:
        if not dao.check_student_enough_credits_in_semester(student.id, semester_id):
            for reg in student.registrations:
                if reg.semester_id == semester_id:
                    dao.system_cancel_registration(reg)

    semester.is_auto_cancelled = True
    db.session.commit()

