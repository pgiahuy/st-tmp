from flask import request, jsonify
from flask_login import login_required, current_user

from course import dao, app





@app.route('/api/course-register', methods=['POST'])
@login_required
def register_course():
    data = request.get_json()
    mssv = current_user.username
    student = dao.get_student_by_mssv(mssv)
    if not student:
        return jsonify({"success": False, "message": "Sinh viên không tồn tại"}), 400
    student_id = student.id
    course_class_id = int(data['course_class_id'])

    print("student_id:", student_id)
    print("course_class_id:",course_class_id)
    action = data.get('action')
    try:
        if action == 'register':
            dao.register_course(student_id, course_class_id)
        elif action == 'unregister':
            dao.unregister_course(student_id, course_class_id)

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@app.route('/api/register-course/confirm', methods=['POST'])
@login_required
def confirm_register():
    data = request.get_json()
    mssv = current_user.username
    student = dao.get_student_by_mssv(mssv)
    if not student:
        return jsonify({"success": False, "message": "Sinh viên không tồn tại"}), 400
    student_id = student.id

    try:
        dao.confirm_registration(student_id)

        return jsonify({
            "success": True,
            "message": "Đủ điều kiện đăng ký"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

@app.route('/api/course-register/<int:course_class_id>', methods=['DELETE'])
@login_required
def unregister_course_route(course_class_id):
    mssv = current_user.username
    student = dao.get_student_by_mssv(mssv)
    if not student:
        return jsonify({"success": False, "message": "Sinh viên không tồn tại"}), 400
    student_id = student.id

    try:
        dao.unregister_course(student_id, course_class_id)
        return jsonify({
            "success": True
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
