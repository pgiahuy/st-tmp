import io

from flask import request, jsonify
from flask_login import login_required, current_user

import course.services.registration_service
from course import dao, app
from course.exceptions import BusinessException
from course.services import registration_service

def register_api(app):
    @app.route('/api/course-register', methods=['POST'])
    def register_course_api():
        if not current_user.is_authenticated:
            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 401
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
            registration_service.register_course(semester_id, student_id, course_class_id)
            return jsonify({
                "success": True
            }), 200

        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

    @app.route('/api/register-course/confirm', methods=['POST'])
    def confirm_register():
        if not current_user.is_authenticated:
            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 401
        mssv = current_user.username
        student = dao.get_student_by_mssv(mssv)
        if not student:
            return jsonify({"success": False, "message": "Sinh viên không tồn tại"}), 400
        student_id = student.id
        semester = dao.get_registration_semester()

        if not semester:
            return jsonify({"success": False, "message": "Không có học kỳ"}), 400
        semester_id = semester.id

        try:
            course.services.registration_service.confirm_registration(semester_id ,student_id)

            return jsonify({
                "success": True,
                "message": "Đủ điều kiện đăng ký",
                "semester_id": semester_id
            }), 200

        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

    @app.route('/api/course-register/<int:course_class_id>', methods=['DELETE'])
    def unregister_course_route(course_class_id):
        if not current_user.is_authenticated:
            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 401
        mssv = current_user.username
        semester_id = dao.get_registration_semester().id
        student = dao.get_student_by_mssv(mssv)
        if not student:
            return jsonify({"success": False, "message": "Sinh viên không tồn tại"}), 400
        student_id = student.id

        try:
            registration_service.cancel_registration(semester_id, student_id, course_class_id)

            return jsonify({
                "success": True
            }), 200
        except BusinessException as e:
            return jsonify({"success": False, "message": str(e)}), 400

