import pytest
from cloudinary.provisioning import Role

from course.dao import auth_user, hash_password, validate_auth
from course.models import User
from course.tests.unit_test.test_base import test_app,test_session

@pytest.fixture
def sample_user(test_session):
    user = User(username="admin",password=hash_password("admin"))
    user.role = "ADMIN"
    test_session.add(user)
    test_session.commit()
    return user

class TestValidateAuth:

    def test_empty_username(self):
        with pytest.raises(ValueError):
            validate_auth("", "123")

    def test_empty_password(self):
        with pytest.raises(ValueError):
            validate_auth("admin", "")

    def test_none_username(self):
        with pytest.raises(ValueError):
            validate_auth(None, "123")

    def test_none_password(self):
        with pytest.raises(ValueError):
            validate_auth("admin", None)

    def test_invalid_type_username(self):
        with pytest.raises(ValueError):
            validate_auth(123, "None")

    def test_invalid_type_password(self):
        with pytest.raises(ValueError):
            validate_auth("admin", 123)

    def test_username_whitespace(self):
        with pytest.raises(ValueError):
            validate_auth("   ", "123")

    def test_password_whitespace(self):
        with pytest.raises(ValueError):
            validate_auth("admin", "   ")

    def test_success(self):
        result = validate_auth("admin", "Abc1234@")
        assert result is None




class TestLogin:

    def test_login_success(self, test_session, sample_user):
        user = auth_user("admin", "admin", test_session)
        assert user is not None
        assert user.username == "admin"

    def test_login_empty_username(self, test_session):
        with pytest.raises(ValueError):
            auth_user("", "admin", test_session)

    def test_login_empty_password(self, test_session, sample_user):
        with pytest.raises(ValueError):
            auth_user("admin", "", test_session)

    def test_login_none_username(self, test_session):
        with pytest.raises(ValueError):
            auth_user(None, "admin", test_session)

    def test_login_none_password(self, test_session, sample_user):
        with pytest.raises(ValueError):
            auth_user("admin", None, test_session)

    def test_username_whitespace(self, test_session):
        with pytest.raises(ValueError):
            auth_user("   ", "admin", test_session)

    def test_password_whitespace(self, test_session):
        with pytest.raises(ValueError):
            auth_user("admin", "   ", test_session)

    def test_password_with_spaces(self, test_session, sample_user):
        user = auth_user("admin", " admin   ", test_session)
        assert user is not None
        assert user.username == "admin"

    def test_username_with_spaces(self, test_session, sample_user):
        user = auth_user("  admin  ", "admin", test_session)
        assert user is not None
        assert user.username == "admin"

    def test_login_wrong_password(self, test_session, sample_user):
        user = auth_user("admin", "123456", test_session)
        assert user is None

    def test_user_not_found(self, test_session):
        user = auth_user("gaihuy", "admin", test_session)
        assert user is None

    def test_login_upper_case(self,test_session, sample_user):
        user = auth_user("Admin", "admin", test_session)
        assert user is not None
        assert user.username == "admin"

    def test_multiple_users(self,test_session):


        u1 = User(username="user1", password=hash_password("123"))
        u2 = User(username="user2", password=hash_password("123"))

        test_session.add_all([u1, u2])
        test_session.commit()

        user = auth_user("user1", "123", test_session)
        assert user.username == "user1"

    def test_sql_injection_username(self,test_session):
        user = auth_user("' OR 1=1 --", "admin", test_session)
        assert user is None

    def test_sql_injection_password(self,test_session):
        user = auth_user("admin", "' OR 1=1 --", test_session)
        assert user is None