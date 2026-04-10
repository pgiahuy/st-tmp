import pytest

from course.dao import hash_password, register_course
from course.models import User
from course.tests.unit_test.test_base import test_app,test_session


@pytest.fixture
def sample(test_session):
    user = User(username="2351050061",password=hash_password("Abc1234@"))
    test_session.add(user)
    test_session.commit()
    return user


def test_registration_success(test_session,sample_user):
    pass