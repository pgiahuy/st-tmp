from flask import render_template, request, session
from werkzeug.utils import redirect

from course import app, dao, login, db, api

from flask_login import logout_user, login_user, current_user, login_required, login_required
from course.models import UserRole, Day, Session


@app.route('/')
def index():
    print(current_user)
    return render_template('index.html')

# @app.route('/admin/login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = dao.auth_user(username=username, password=password ,session=db.session)
#         if user and user.role == UserRole.ADMIN:
#             login_user(user)
#             return redirect('/admin')
#         return render_template('admin/login.html', err_msg='Sai tài khoản hoặc không phải admin!')
#     return render_template('admin/login.html')

import re

@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    err_msg = None
    username = None
    role = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role')

        if not username or not password:
            err_msg = "Vui lòng nhập đầy đủ tài khoản và mật khẩu!"
            return render_template('login.html', err_msg=err_msg, roles=UserRole)

        if not role:
            err_msg = "Vui lòng chọn vai trò!"
            return render_template('login.html', err_msg=err_msg, roles=UserRole)

        if role == "USER":
            if not re.fullmatch(r"\d{10}", username):
                err_msg = "Mã số sinh viên phải là 10 chữ số!"
                return render_template('login.html', err_msg=err_msg, roles=UserRole)

        user = dao.auth_user(username, password, session=db.session, role=role)

        if user is None:
            err_msg = "Sai tài khoản hoặc mật khẩu!"
        else:
            login_user(user)
            return redirect("/" if user.role == UserRole.USER else "/admin")

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
    student = dao.get_student_by_mssv(current_user.student.mssv)
    student_classes = dao.get_course_classes_for_student(student.id)
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

    kw = request.args.get('kw')
    course_id = request.args.get('course_id')

    student = dao.get_student_by_mssv(current_user.username)

    course_classes = dao.get_course_classes(course_id=course_id, kw=kw)
    course_classes_in_semester = dao.get_course_classes()


    registered_ids = [reg.course_class_id for reg in student.registrations
                      if reg.semester_id == dao.get_current_semester().id]

    return render_template(
        'register_course.html',
        course_classes_in_semester = course_classes_in_semester,
        selected_course_id=course_id,
        course_classes=course_classes,
        registered_ids=registered_ids,
        student_classes=dao.get_course_classes_for_student(student.id)
    )


@app.route('/timetable')
@login_required
def timetable_page():
    current_semester = dao.get_current_semester()
    semester_name = f"{current_semester.name} - {current_semester.year}"
    student = dao.get_student_by_mssv(current_user.username)

    student_classes = dao.get_course_classes_for_student(student.id)

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