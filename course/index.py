from datetime import datetime

from flask import render_template, request, session, abort, jsonify
from werkzeug.utils import redirect

from course import app, dao, login, db, api

from flask_login import logout_user, login_user, current_user, login_required, login_required
from course.models import UserRole, Day, Session
from course.services import auth_service


def register_routes(app):
    @app.before_request
    def restrict_admin_access():
        if not current_user.is_authenticated:
            return

        if current_user.role == UserRole.ADMIN:
            if request.path == '/':
                return
            allowed_paths = ['/admin', '/logout', '/login', '/static', "/api/admin"]

            if any(request.path.startswith(p) for p in allowed_paths):
                return
            abort(403)


    @app.errorhandler(401)
    def unauthorized(error):
        return render_template('error/401.html'), 401

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("error/403.html"), 403

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

    @app.route('/receipt/<int:semester_id>')
    @login_required
    def receipt(semester_id):
        student = dao.get_student_by_mssv(current_user.username)

        classes = dao.get_course_classes_student_registered(
            semester_id=semester_id,
            student_id=student.id
        )
        sum_credits = sum(c.course.credits for c in classes)

        return render_template(
            'receipt.html',
            student=student,
            sum_credits=sum_credits,
            semester=dao.get_semester_by_id(semester_id),
            now=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            classes=classes
        )

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
        student_classes = dao.get_course_classes_student_registered(reg_semester.id, student.id)

        sum_credits = sum(c.course.credits for c in student_classes)

        return render_template('profile.html',
                               sum_credits=sum_credits,
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
                try:
                    auth_service.change_password(
                        current_user.id,
                        old_password,
                        new_password
                    )
                    success_msg = "Đổi mật khẩu thành công!"
                except Exception as e:
                    err_msg = str(e)
                # result = dao.change_password(
                #     current_user.id,
                #     old_password,
                #     new_password
                # )



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

        sum_credits = sum(c.course.credits for c in registered_course_class)
        return render_template(
            'register_course.html',
            courses_in_reg_semester=courses,
            selected_course_id=course_id,
            course_classes_in_reg_semester=course_classes,
            sum_credits=sum_credits,
            registered_ids=registered_ids,
            registered_course_class=registered_course_class,

            registration_semester=reg_semester
        )

    @app.route('/timetable')
    @login_required
    def timetable_page():
        reg_semester = dao.get_registration_semester()
        student = dao.get_student_by_mssv(current_user.username)
        student_classes = dao.get_course_classes_student_registered(reg_semester.id, student.id)

        semester_name = f"{reg_semester.name} - {reg_semester.year}"

        days = [
            {"name": d.label, "value": d}
            for d in Day
        ]

        sessions = [
            {"name": s.display, "value": s}
            for s in Session
        ]

        sum_credits = sum(c.course.credits for c in student_classes)

        return render_template('timetable.html',
                               student_classes=student_classes,
                               semester_name=semester_name,
                               sum_credits=sum_credits,
                               days=days,
                               sessions=sessions)


if __name__ == "__main__":
    app.run(debug=True, port=5000)