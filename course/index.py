from datetime import datetime, date, timedelta

from flask import render_template, request, session, abort, jsonify
from werkzeug.utils import redirect

from course import app, dao, login, db, api

from flask_login import logout_user, login_user, current_user, login_required, login_required
from course.models import UserRole, Day, Session, ConfigEnum
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
        current_semester = dao.get_current_semester()

        semester_for_view = current_semester or reg_semester
        if not semester_for_view:
            semester_for_view = dao.get_recent_past_semester()


        student = dao.get_student_by_mssv(current_user.username)

        if not semester_for_view:
            error_msg = "Danh sách môn trống!"
            return render_template('profile.html',
                                   student=student,
                                   error_msg = error_msg)

        student_classes = dao.get_course_classes_student_registered(semester_for_view.id, student.id)

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
        error_msg = None
        reg_semester_tmp = dao.get_registration_semester()
        reg_semester = reg_semester_tmp
        is_preview = False

        if not reg_semester_tmp:
            preview_sem = dao.get_review_registration_semester()
            next_semester = dao.get_next_semester()
            current_semester = dao.get_current_semester()
            dl = dao.get_config_value(ConfigEnum.CANCEL_DEADLINE_DAYS, 14)

            if current_semester:
                if date.today() < current_semester.start_date + timedelta(days=dl):
                    error_msg = f"Ngoài thời gian đăng ký! {current_semester.name} - {current_semester.year} đã đóng vào {current_semester.end_registration_date}"
                elif next_semester:
                    error_msg = f"Ngoài thời gian đăng ký! {next_semester.name} - {next_semester.year}  mở vào {next_semester.start_registration_date}"

                else:
                    error_msg = "Ngoài thời gian đăng ký!"
            elif preview_sem:
                error_msg = f"Ngoài thời gian đăng ký! {preview_sem.name} - {preview_sem.year}  mở vào {preview_sem.start_registration_date}"
            else:
                error_msg = "Ngoài thời gian đăng ký!"

            if preview_sem:
                reg_semester = preview_sem
                is_preview = True
            else:
                pass

        current_semester = dao.get_current_semester()

        semester_for_view = reg_semester or current_semester

        if not semester_for_view:
            return render_template('register_course.html', error=error_msg)



        kw = request.args.get('kw')
        course_id = request.args.get('course_id')

        student = dao.get_student_by_mssv(current_user.username)

        course_classes = dao.get_course_classes_in_reg_semester(semester_id= semester_for_view.id, course_id=course_id, kw=kw)
        courses = dao.get_courses_by_current_reg_semester(semester_id=semester_for_view.id)

        registered_ids = dao.get_course_class_ids_student_registered(semester_id=semester_for_view.id, student_id=student.id)

        registered_course_class = dao.get_course_classes_student_registered(semester_id=semester_for_view.id,
                                                                            student_id=student.id)
        print("========================")
        print(student.full_name)
        print(semester_for_view.name)
        print(dao.get_course_classes_student_registered(student_id=student.id, semester_id=semester_for_view.id))

        sum_credits = sum(c.course.credits for c in registered_course_class)
        print("&&&&&&&&&&&")
        print("====reg_semester= =", semester_for_view)

        valid_regis = (not is_preview) and (reg_semester_tmp is not None)
        return render_template(
            'register_course.html',
            courses_in_reg_semester=courses,
            selected_course_id=course_id,
            course_classes_in_reg_semester=course_classes,
            sum_credits=sum_credits,
            registered_ids=registered_ids,
            registered_course_class=registered_course_class,
            registration_semester=semester_for_view,
            valid_regis=valid_regis,
            is_preview=is_preview,
            error=error_msg
        )

    @app.route('/timetable')
    @login_required
    def timetable_page():
        reg_semester = dao.get_registration_semester()
        current_semester = dao.get_current_semester()
        days = [
            {"name": d.label, "value": d}
            for d in Day
        ]

        sessions = [
            {"name": s.display, "value": s}
            for s in Session
        ]

        semester_for_view = current_semester or reg_semester
        if not semester_for_view:
            semester_for_view = dao.get_recent_past_semester()

        if not semester_for_view:
            error_msg = "Thời khoá biểu trống!"
            return render_template('timetable.html',
                                   error_msg = error_msg,
                                   days=days,
                                   sessions=sessions
                                   )

        student = dao.get_student_by_mssv(current_user.username)
        student_classes = dao.get_course_classes_student_registered(semester_for_view.id, student.id)

        semester_name = f"{semester_for_view.name} - {semester_for_view.year}"


        sum_credits = sum(c.course.credits for c in student_classes)

        return render_template('timetable.html',
                               student_classes=student_classes,
                               semester_name=semester_name,
                               sum_credits=sum_credits,
                               days=days,
                               sessions=sessions)


if __name__ == "__main__":
    app.run(debug=True, port=5000)