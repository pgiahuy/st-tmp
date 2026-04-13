class BusinessException(Exception):
    def __init__(self, code, message=None):
        self.code = code
        self.message = message or code
        super().__init__(self.message)


class WeakPasswordException(BusinessException):
    def __init__(self, message):
        super().__init__("WEAK_PASSWORD", message)

class UserNotFoundException(BusinessException):
    def __init__(self):
        super().__init__("USER_NOT_FOUND", "User không tồn tại")


class InvalidOldPasswordException(BusinessException):
    def __init__(self):
        super().__init__("INVALID_OLD_PASSWORD", "Mật khẩu cũ không đúng")