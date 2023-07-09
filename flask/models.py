from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()
login_manager = LoginManager()

class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    passwordHash = db.Column(db.String(128), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    
    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)
    
    def checkPassword(self, password):
        return check_password_hash(self.passwordHash, password)
    
    def __repr__(self):
        return f'user_id_{self.id}'
    
class TriviaQuestionModel(UserMixin, db.Model):
    question_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    question = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    

@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
