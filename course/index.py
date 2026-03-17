from flask import render_template, request
from werkzeug.utils import redirect

from course import app, dao, login

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    err_msg = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username, password)
        if user:
            load_user(user)
            return redirect("/")
        else:
            err_msg = "Mã số sinh viên hoặc mật khẩu không đúng!"
    return render_template('login.html', err_msg=err_msg)

@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)

if __name__ == "__main__":
    app.run(debug=True, port=5000)