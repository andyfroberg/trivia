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

    



    # def load_trivia_questions():
    #     questions = {
    #         'q1': {
    #             'id': 1,
    #             'question': 'What is the capital of Washington state?',
    #             'answer': 'Olympia'
    #         },
    #         'q2': {
    #             'id': 2,
    #             'question': 'How many breweries are there in Washington state?',
    #             'answer': '423'
    #         },
    #         'q3': {
    #             'id': 3,
    #             'question': 'In what two states is the Hoover dam located?',
    #             'answer': ['Nevada', 'Arizona']
    #         },
    #     }
    #     # for question in questions.values():
    #     #     trivia_question = TriviaQuestionModel()
    #     #     trivia_question.id = question['id']
    #     #     trivia_question.question = question['question']
    #     #     trivia_question.answer = question['answer']
    #     #     db.session.add(trivia_question)
    #     #     db.session.commit()
    #     with app.app_context():
    #         trivia_question = TriviaQuestionModel()
    #         trivia_question.id = questions['q1']['id']
    #         trivia_question.question = questions['q1']['question']
    #         trivia_question.answer = questions['q1']['answer']
    #         db.session.add(trivia_question)
    #         db.session.commit()

    # def get_random_questions():
    #     # API endpoint URL
    #     api_url = "https://the-trivia-api.com/v2/questions"
    #     # Parameters for the API request
    #     params = {}
    #     headers = {}  # Free tier - no API key needed
    #     try:
    #         response = requests.get(api_url, headers=headers, params=params)
    #         # Raise an exception if the request was unsuccessful
    #         response.raise_for_status()
    #         # Parse the response JSON
    #         data = response.json()
    #     except requests.exceptions.HTTPError as e:
    #         flash('A connection error occurred.', 'alert-danger')
    #     except Exception as e:
    #         flash('An error occurred.', 'alert-danger')
    #     if not data:
    #         return None
    #     return data


    # def get_question_from_api(category=''):
    #     categories = [
    #         'artliterature',
    #         'language',
    #         'sciencenature',
    #         'general',
    #         'fooddrink',
    #         'peopleplaces',
    #         'geography',
    #         'historyholidays',
    #         'entertainment',
    #         'toysgames',
    #         'music',
    #         'mathematics',
    #         'religionmythology',
    #         'sportsleisure'
    #     ]
    #     api_url = f'https://api.api-ninjas.com/v1/trivia?category={category}'
    #     response = requests.get(api_url, headers={'X-Api-Key': 'IF8SxeQZrS0hn1pl7fSbHxvK5uscG5dhPFQVlsyI'})
    #     if response.status_code == requests.codes.ok:
    #         return response.json()
    #     else:
    #         flash('An error occurred.', 'alert-danger')
    #         return response.status_code, response.text