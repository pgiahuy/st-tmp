from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager


app = Flask(__name__, template_folder='templates')

app.secret_key = 'isufheoihfeuheiohmioanwn'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/coursedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["MAX"] = True
db = SQLAlchemy(app=app)
login = LoginManager(app=app)



cloudinary.config(
    cloud_name='dslzjm9y1',
    api_key='378681865892523',
    api_secret='JoV-kP2mQAXaW3dfDlQAuuqP7pA'
)