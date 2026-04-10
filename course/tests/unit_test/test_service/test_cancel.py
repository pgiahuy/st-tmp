import pytest

from course.dao import auth_user, hash_password
from course.models import User
from course.tests.unit_test.test_base import test_app,test_session
