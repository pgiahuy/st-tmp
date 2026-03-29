from flask import render_template, request, session
from werkzeug.utils import redirect

from course import app, dao, login, db

from flask_login import logout_user, login_user, current_user, login_required, login_required
from course.models import UserRole


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password ,session=db.session)

        if user and user.role == UserRole.ADMIN:
            login_user(user)
            return redirect('/admin')

        return render_template('admin/login.html', err_msg='Sai tài khoản hoặc không phải admin!')

    return render_template('admin/login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    err_msg = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username, password, session=db.session)
        if user:
            login_user(user)
            return redirect("/")
        else:
            err_msg = "Mã số sinh viên hoặc mật khẩu không đúng!"

    return render_template('login.html', err_msg=err_msg)

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route('/userinfo')
def my_profile():
    student = dao.get_student_by_id(current_user.student)

    return render_template('profile.html', student=student)
    


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
  
@app.route('/register-course', methods=['GET', 'POST'])
@login_required
def register_course():
    courses = dao.get_courses()

    course_id = request.args.get('course_id')

    selected_course_id = course_id
    selected_filter_type = request.args.get('filter_type', '')

    classes = dao.get_course_classes(course_id=course_id)

    return render_template('register_course.html',
                           courses=courses,
                           classes=classes,
                           selected_course_id = selected_course_id,
                           selected_filter_type = selected_filter_type)


if __name__ == "__main__":
    app.run(debug=True, port=5000)