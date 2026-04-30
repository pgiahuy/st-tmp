import pytest
from flask import Flask
from flask_login import LoginManager, login_manager

from course import db, index, api
from course.admin import admin
from course.models import UserRole, User


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config['PAGE_SIZE'] = 2
    app.config['TESTING'] = True
    app.secret_key = 'hduageifghegehsghe8ghe8ghe89ye8a9y'
    db.init_app(app)
    admin.init_app(app)
    index.register_routes(app)
    api.register_api(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User.query.get(user_id)

    return app


@pytest.fixture
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

#
# @pytest.fixture
# def test_app():
#     app = create_app()
#     ctx = app.app_context()
#     ctx.push()
#     db.create_all()
#     yield app
#     db.session.remove()
#     db.drop_all()
#     ctx.pop()


@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()



@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


# @pytest.fixture
# def mock_cloudinary(monkeypatch):
#     def fake_upload(file):
#         return {'secure_url':'https://img.png'}
#
#     monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)



