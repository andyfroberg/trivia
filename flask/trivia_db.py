from flask_sqlalchemy import SQLAlchemy
from models import db, login_manager, UserModel, TriviaQuestionModel


class TriviaDB:
    def __init__(self, flask_app):
        self.db = SQLAlchemy()
        
        # Initialize the database
        db.init_app(flask_app)
        with flask_app.app_context():
            self.db.create_all()
    
    def load_trivia_questions(self):
        pass