import pytest

from course.dao import auth_user, hash_password
from course.models import User
from course.tests.unit.test_base import test_app,test_session

@pytest.fixture
def sample_user(test_session):
    user = User(username="admin",password=hash_password("admin"))
    test_session.add(user)
    test_session.commit()
    return user

def test_login_success(test_session, sample_user):
    user = auth_user("admin", "admin", test_session)
    assert user is not None
    assert user.username == "admin"

def test_login_wrong_password(test_session, sample_user):
    user = auth_user("admin", "123456", test_session)
    assert user is None

def test_login_empty_username(test_session):
    with pytest.raises(Exception):
        auth_user("", "admin", test_session)



def test_login_empty_password(test_session, sample_user):
    with pytest.raises(Exception):
        auth_user("admin", "", test_session)


def test_login_none_username(test_session):
    with pytest.raises(Exception):
     auth_user(None, "admin", test_session)


def test_login_none_password(test_session, sample_user):
    with pytest.raises(Exception):
        user = auth_user("admin", None, test_session)


def test_login_case(test_session, sample_user):
    user = auth_user("Admin", "admin", test_session)
    assert user is None

def test_multiple_users(test_session):
    u1 = User(username="user1", password=hash_password("123"))
    u2 = User(username="admin", password=hash_password("admin"))

    test_session.add_all([u1, u2])
    test_session.commit()

    user = auth_user("admin", "admin", test_session)

    assert user.username == "admin"

def test_sql_injection(test_session):
    user = auth_user("' OR 1=1 --", "admin", test_session)

    assert user is None