# from flask_login import UserMixin, LoginManager
import flask_login
# from werkzeug.security import generate_password_hash, check_password_hash
import werkzeug.security
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()
login_manager = flask_login.LoginManager()

class UserModel(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    current_question = db.Column(db.Integer, nullable=False)
    score_current_round = db.Column(db.Integer)
    score_lifetime = db.Column(db.Integer)
    profile_picture = db.Column(db.String(128))  # URI to image stored in s3
    profile_bio = db.Column(db.String(512))
    
    def set_password(self, password):
        self.password_hash = werkzeug.security.generate_password_hash(password)
    
    def check_password(self, password):
        return werkzeug.security.check_password_hash(self.password_hash, password)
    
    def __repr__(self):  # Add repr, str, etc. dunders for all classes?
        return f'user_id_{self.id}'
    
class TriviaQuestionModel(flask_login.UserMixin, db.Model):
    question_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    category = db.Column(db.String(64), nullable=False)
    difficulty = db.Column(db.String(64), nullable=False)
    question = db.Column(db.String(128), nullable=False)
    correct_answer = db.Column(db.String(128), nullable=False)
    # hint = db.Column(db.String(128), nullable=False)
    count_attempted = db.Column(db.Integer)
    count_answered_correctly = db.Column(db.Integer)

@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))