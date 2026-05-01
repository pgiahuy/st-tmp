from flask import request, jsonify
from flask_login import login_required, current_user

import course.services.registration_service
from course import dao, app, db
from course.exceptions import BusinessException
from course.models import UserRole, CourseClassScheduleRoom, Room
from course.services import registration_service

from course.services.system_cancel_service import auto_cancel_job

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
        reg_semester = dao.get_registration_semester()
        current_semester = dao.get_current_semester()

        semester = reg_semester or current_semester

        semester_id = semester.id

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

    @app.route("/api/admin/available-rooms")
    def available_rooms():
        slot_ids = request.args.get("slot_ids")
        semester_id = request.args.get("semester_id")

        if not slot_ids or not semester_id:
            return jsonify([])

        slot_ids = [int(x) for x in slot_ids.split(",")]
        semester_id = int(semester_id)

        busy_room_ids = (
            db.session.query(CourseClassScheduleRoom.room_id)
            .filter(
                CourseClassScheduleRoom.slot_id.in_(slot_ids),
                CourseClassScheduleRoom.semester_id == semester_id
            )
            .distinct()
        )

        rooms = Room.query.filter(~Room.id.in_(busy_room_ids)).all()

        return jsonify([
            {"id": r.id, "name": r.name}
            for r in rooms
        ])

#
# @app.route('/api/admin/auto-cancel', methods=['POST'])
# def api_auto_cancel():
#     print("===================")
#     print("ADMIN ROLEE==============", current_user.role)
#     if not current_user.is_authenticated:
#         return jsonify({
#             "success": False,
#             "message": "Unauthorized"
#         }), 401
#
#     if current_user.role != UserRole.ADMIN:
#         return jsonify({
#             "success": False,
#             "message": "Permission Denied"
#         }), 403
#
#     try:
#         auto_cancel_job()
#         return jsonify({
#             "message": "Đã tự động huỷ đăng ký các sinh viên không đăng ký đủ tín chỉ"
#         }), 200
#
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#         }), 500