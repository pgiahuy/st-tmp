# from functools import wraps
# from flask import abort
# from flask_login import current_user
#
# from course.models import UserRole

#
# def student_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_authenticated:
#             abort(401)
#         if current_user.role != UserRole.USER:
#             abort(403)
#         return f(*args, **kwargs)
#     return decorated_function