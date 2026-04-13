from course import dao
from course.exceptions import UserNotFoundException, InvalidOldPasswordException, WeakPasswordException


def validate_new_password(password: str):
    if len(password) < 8:
        raise WeakPasswordException("Mật khẩu phải >= 8 ký tự")

    if not any(c.isupper() for c in password):
        raise WeakPasswordException("Mật khẩu phải có chữ hoa")

    if not any(c.islower() for c in password):
        raise WeakPasswordException("Mật khẩu phải có chữ thường")

    if not any(c.isdigit() for c in password):
        raise WeakPasswordException("Mật khẩu phải có số")

    if not any(c in "!@#$%^&*()" for c in password):
        raise WeakPasswordException("Mật khẩu phải có ký tự đặc biệt")


def change_password(user_id, old_password, new_password):
    user = dao.get_user_by_id(user_id)

    if not user:
        raise UserNotFoundException()

    if not dao.auth_user(user.username, old_password):
        raise InvalidOldPasswordException()

    validate_new_password(new_password)

    dao.change_password(user_id, new_password)

    return True