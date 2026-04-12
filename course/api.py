from flask import request, jsonify
from flask_login import login_required, current_user

import course.services.registration_service
from course import dao, app
from course.services import registration_service


@app.route('/api/course-register', methods=['POST'])
@login_required
def register_course_api():
    data = request.get_json()

    if not data or "course_class_id" not in data:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    mssv = current_user.username
    student_id = dao.get_student_id_by_mssv(mssv)

    if not student_id:
        return jsonify({"success": False, "message": "Sinh viên không tồn tại"}), 400

    course_class_id = int(data['course_class_id'])
    semester_id = dao.get_registration_semester().id

    try:
        registration_service.register_course(semester_id,student_id, course_class_id)
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
    mssv = current_user.username
    student = dao.get_student_by_mssv(mssv)
    if not student:
        return jsonify({"success": False, "message": "Sinh viên không tồn tại"}), 400
    student_id = student.id

    try:
        course.services.registration_service.confirm_registration(student_id)

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
