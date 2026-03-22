from flask import render_template, request
from werkzeug.utils import redirect

from course import app, dao, login
from flask_login import logout_user,login_user

from course.models import UserRole


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)

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
        user = dao.auth_user(username, password)
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

@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)

if __name__ == "__main__":
    app.run(debug=True, port=5000)