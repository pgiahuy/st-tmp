from flask import render_template, request, session
from werkzeug.utils import redirect

from course import app, dao, login, db, api

from flask_login import logout_user, login_user, current_user, login_required, login_required
from course.models import UserRole, Day, Session


def register_routes(app):

    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


    @app.route('/')
    def index():
        print(current_user)
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login_my_user():
        err_msg = None
        username = None

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            try:
                user = dao.auth_user(username, password)
                if user:
                    login_user(user)
                    return redirect('/admin' if user.role == UserRole.ADMIN else '/')

                else:
                    err_msg = 'Sai tên đăng nhập hoặc mật khẩu!'
            except Exception as e:
                err_msg = str(e)

        return render_template('login.html',
                               err_msg=err_msg,
                               old_username=username,
                               )

    @app.route("/logout")
    @login_required
    def logout_my_user():
        logout_user()
        session.clear()
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

        registered_ids = dao.get_course_class_ids_student_registered(semester_id=reg_semester.id, student_id=student.id)

        registered_course_class = dao.get_course_classes_student_registered(semester_id=reg_semester.id,
                                                                            student_id=student.id)
        print("========================")
        print(student.full_name)
        print(reg_semester.name)
        print(dao.get_course_classes_student_registered(student_id=student.id, semester_id=reg_semester.id))
        return render_template(
            'register_course.html',
            courses_in_reg_semester=courses,
            selected_course_id=course_id,
            course_classes_in_reg_semester=course_classes,
            registered_ids=registered_ids,
            registered_course_class=registered_course_class,

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