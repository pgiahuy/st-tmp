import pytest

from course.dao import auth_user, hash_password, count_course_registrations
from course.models import User
from course.tests.unit_test.test_base import test_app,test_session



