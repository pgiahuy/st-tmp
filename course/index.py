from flask import render_template, request, session
from werkzeug.utils import redirect

from course import app, dao, login, db
from flask_login import logout_user,login_user, login_required, current_user
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

from flask import session, jsonify

@app.route('/userinfo')
def my_profile():
    user_id = session.get('user_id')
    print(user_id)
    # if not user_id:
    #     return jsonify({"error": "Chưa đăng nhập"}), 401
    #
    # user = User.query.get(user_id)
    #
    # return jsonify({
    #     "id": user.id,
    #     "username": user.username
    # })

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

        # check confirm password
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)