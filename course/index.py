from flask import render_template, request, session
from werkzeug.utils import redirect

from course import app, dao, login, db, api

from flask_login import logout_user, login_user, current_user, login_required, login_required
from course.models import UserRole, Day, Session



@app.route('/')
def index():
    print(current_user)
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    err_msg = None
    username = None
    role = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role')
        try:
            user = dao.auth_user(username, password, session=db.session, role=role)
            if user:
                login_user(user)
                return redirect('/' if user.role == UserRole.USER else '/admin')

            else:
                err_msg = 'Sai username hoặc password!'
        except Exception as e:
            err_msg = str(e)

    return render_template('login.html',
                           err_msg=err_msg,
                           roles=UserRole,
                           old_username=username,
                           old_role=role
                           )



@app.route("/logout")
@login_required
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route('/userinfo')
@login_required
def my_profile():
    reg_semester = dao.get_registration_semester()
    student = dao.get_student_by_mssv(current_user.username)
    student_classes = [reg.course_class for reg in student.registrations
                       if reg.semester_id == reg_semester.id]
    return render_template('profile.html',
                           student=student,
                           student_classes=student_classes)
    


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    err_msg = None
    success_msg = None

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            err_msg = "Mật khẩu xác nhận không khớp!"
        else:
            result = dao.change_password(
                current_user.id,
                old_password,
                new_password
            )

            if "error" in result:
                err_msg = result["error"]
            else:
                success_msg = "Đổi mật khẩu thành công!"

    return render_template(
        'change_password.html',
        err_msg=err_msg,
        success_msg=success_msg
    )

@app.route('/register-course')
@login_required
def register_course_page():

    reg_semester = dao.get_registration_semester()
    if not reg_semester:
        return render_template('register_course.html', error="Hiện không trong thời gian đăng ký học phần.")

    kw = request.args.get('kw')
    course_id = request.args.get('course_id')

    student = dao.get_student_by_mssv(current_user.username)

    course_classes = dao.get_course_classes_in_reg_semester(course_id=course_id, kw=kw)
    courses = dao.get_courses_by_current_reg_semester()

    registered_ids = [reg.course_class_id for reg in student.registrations
                      if reg.semester_id == reg_semester.id]


    student_classes = [reg.course_class for reg in student.registrations
                       if reg.semester_id == reg_semester.id]

    return render_template(
        'register_course.html',
        courses_in_reg_semester=courses,
        selected_course_id=course_id,
        course_classes_in_reg_semester=course_classes,
        registered_ids=registered_ids,
        student_classes=student_classes,
        registration_semester=reg_semester
    )

@app.route('/timetable')
@login_required
def timetable_page():
    reg_semester = dao.get_registration_semester()
    student = dao.get_student_by_mssv(current_user.username)
    student_classes = [reg.course_class for reg in student.registrations
                       if reg.semester_id == reg_semester.id]


    semester_name = f"{reg_semester.name} - {reg_semester.year}"




    days = [
        {"name": "Thứ 2", "value": Day.MONDAY},
        {"name": "Thứ 3", "value": Day.TUESDAY},
        {"name": "Thứ 4", "value": Day.WEDNESDAY},
        {"name": "Thứ 5", "value": Day.THURSDAY},
        {"name": "Thứ 6", "value": Day.FRIDAY},
        {"name": "Thứ 7", "value": Day.SATURDAY},
    ]

    sessions = [
        {"name": Session.MORNING.display, "value": Session.MORNING},
        {"name": Session.AFTERNOON.display, "value": Session.AFTERNOON},
        {"name": Session.EVENING.display, "value": Session.EVENING},
    ]

    return render_template('timetable.html',
                           student_classes=student_classes,
                           semester_name=semester_name,
                           days=days,
                           sessions=sessions)




if __name__ == "__main__":
    app.run(debug=True, port=5000)