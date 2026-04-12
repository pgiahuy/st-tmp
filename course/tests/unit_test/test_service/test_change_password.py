import pytest

from course.dao import auth_user, hash_password, validate_auth
from course.exceptions import UserNotFoundException, InvalidOldPasswordException, WeakPasswordException
from course.models import User
from course.services import auth_service
from course.tests.unit_test.test_base import test_app,test_session


@pytest.fixture
def sample_user(test_session):
    user = User(username="2351050061",password=hash_password("Abc1234@"))
    user.role = "USER"
    test_session.add(user)
    test_session.commit()
    return user

def test_change_password_success(test_session, sample_user):
    old_password_plain = "Abc1234@"
    new_password = "Aeg5@aegae"
    auth_service.change_password(sample_user.id,old_password_plain,new_password)

    assert auth_user(sample_user.username,new_password)


def test_change_password_user_not_found(test_session):
    old_password_plain = "Abc1234@"
    new_password = "Aeg5@aegae"
    with pytest.raises(UserNotFoundException):
        auth_service.change_password(3, old_password_plain, new_password)



def test_change_password_wrong_old_password(test_session, sample_user):
    old_password_plain = "Ac1234@"
    new_password = "Aeg5@aegae"
    with pytest.raises(InvalidOldPasswordException):
        auth_service.change_password(sample_user.id, old_password_plain, new_password)


def test_invalid_new_password(test_session, sample_user):
    old_password_plain = "Abc1234@"
    new_password = "adwa"
    with pytest.raises(WeakPasswordException):
        auth_service.change_password(sample_user.id, old_password_plain, new_password)

def test_invalid_new_password_short(test_session, sample_user):
    old_password_plain = "Abc1234@"
    new_password = "adwa"
    with pytest.raises(WeakPasswordException):
        auth_service.change_password(sample_user.id, old_password_plain, new_password)

def test_invalid_new_password_not_upper(test_session, sample_user):
    old_password_plain = "Abc1234@"
    new_password = "adw2367&&a"
    with pytest.raises(WeakPasswordException):
        auth_service.change_password(sample_user.id, old_password_plain, new_password)

def test_invalid_new_password_not_lower(test_session, sample_user):
    old_password_plain = "Abc1234@"
    new_password = "AAAS125378%"
    with pytest.raises(WeakPasswordException):
        auth_service.change_password(sample_user.id, old_password_plain, new_password)

def test_invalid_new_password_not_digit(test_session, sample_user):
    old_password_plain = "Abc1234@"
    new_password = "gagGAUG$$#"
    with pytest.raises(WeakPasswordException):
        auth_service.change_password(sample_user.id, old_password_plain, new_password)

def test_invalid_new_password_not_special(test_session, sample_user):
    old_password_plain = "Abc1234@"
    new_password = "gagGAU12345"
    with pytest.raises(WeakPasswordException):
        auth_service.change_password(sample_user.id, old_password_plain, new_password)