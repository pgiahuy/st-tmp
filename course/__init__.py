from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager


app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = 'isufheoihfeuheiohmioanwn'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/coursedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["MAX"] = True
app.config["DEFAULT_PASSWORD"] = "Abc1234@"
db = SQLAlchemy(app=app)
login = LoginManager(app=app)

from course import admin


cloudinary.config(
    cloud_name='dslzjm9y1',
    api_key='378681865892523',
    api_secret='JoV-kP2mQAXaW3dfDlQAuuqP7pA'
)