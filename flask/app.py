#!/usr/local/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import LoginForm, RegisterForm, PasswordChangeForm, TriviaAnswerForm, UserFilterForm
from flask_login import login_user, logout_user, login_required, current_user
from models import db, login_manager, UserModel, TriviaQuestionModel
from datetime import datetime
import requests
import json

# Create a new Flask application instance
app = Flask(__name__)
app.secret_key = 'secret'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trivia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
with app.app_context():
    db.create_all()

#initialize the login manager
login_manager.init_app(app)

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


def addUser(email, username, password):
    user = UserModel()
    user.setPassword(password)
    user.email = email
    user.username = username
    user.points = 0
    db.session.add(user)
    db.session.commit()

#handler for bad requests
@login_manager.unauthorized_handler
def authHandler():
    form = LoginForm()
    flash('Please login to access this page', 'alert-danger')
    return render_template('login.html',form=form)


@app.route('/')
def home():
    logged_in = False
    user_name = ""
    if current_user.is_authenticated:
        logged_in = True  # Update this based on user authentication status
        user_name = current_user.username
    # This function will be called when someone accesses the root URL
    return render_template('home.html', logged_in=logged_in, user_name=user_name)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Please enter a valid email and password', 'alert-danger')
            return render_template('login.html',form=form)
        user = UserModel.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Please enter a valid email', 'alert-danger')
            return render_template('login.html',form=form)
        if not user.checkPassword(form.password.data):
            flash('Please enter a valid password', 'alert-danger')
            return render_template('login.html',form=form)
        login_user(user)
        session['email'] = form.email.data
        return redirect(url_for('my_trivia', order_by_date=0))
    return render_template("login.html", form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    session.pop('email', None)
    return redirect(url_for('home'))


@app.route('/register', methods=["GET", "POST"])
def register():
    logged_in = False
    user_name = ""
    if current_user.is_authenticated:
        logged_in = True  # Update this based on user authentication status
        user_name = current_user.username
    form = RegisterForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            if form.password.data != form.confirmPassword.data:
                flash('Passwords do not match', 'alert-danger')
            else:
                flash('Something went wrong in registration', 'alert-danger')
            return render_template('register.html',form=form)
        user = UserModel.query.filter_by(email=form.email.data).first()
        if user is None:
            if form.password.data == form.confirmPassword.data:
                addUser(form.email.data, form.username.data, form.password.data)  # Need username validation?
                flash('Registration successful', 'alert-success')
                session['email'] = form.email.data
                user = UserModel.query.filter_by(email=form.email.data).first()
                login_user(user)
                return redirect(url_for('my_trivia', order_by_date=0))  # may need to go back to 'login' if still buggy
            else:
                flash('Passwords do not match', 'alert-danger')
                return render_template('register.html',form=form)
        else:
            flash('Email already registered', 'alert-danger')
            return render_template('register.html',form=form)    
    return render_template('register.html',form=form, logged_in=logged_in, user_name=user_name)


@app.route('/my-trivia', methods=['GET', 'POST'])
def my_trivia():
    answer_form = TriviaAnswerForm()
    logged_in = False
    user_name = ''
    if current_user.is_authenticated:
        logged_in = True
        user_name = current_user.username
        question = get_question_from_api()
        if answer_form.validate_on_submit():
            if request.form['answer'].lower() == question[0]['answer'].lower():
                current_user.points += 1
                db.session.commit()
                flash('Your answer is correct!', 'alert-success')
            else:
                flash(f"Your answer is incorrect. The correct answer was {question[0]['answer']}", 'alert-danger')
        user_score = current_user.points
        return render_template('my-trivia.html', answer_form=answer_form, logged_in=logged_in, 
                               user_name=user_name, question=question, user_score=user_score)
    return render_template("login.html")


@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    user_filter_form = UserFilterForm()
    users = UserModel.query.all()
    logged_in = False
    user_name = ''
    if current_user.is_authenticated:
        logged_in = True
        user_name = current_user.username
    # Check if the user has searched for an event by title
    if user_filter_form.validate_on_submit():
        filtered_users = []
        for user in users:
            if request.form['query'].lower() in str(user.username).lower():
                filtered_users.append(user)
            users = filtered_users
        return render_template('leaderboard.html', user_filter_form=user_filter_form, users=users, logged_in=logged_in, user_name=user_name)
    return render_template('leaderboard.html', user_filter_form=user_filter_form, users=users, logged_in=logged_in, user_name=user_name)


def change_password():
    passwordChangeForm = PasswordChangeForm()
    if current_user.is_authenticated:
        logged_in = True
        user_name = current_user.username
        user = UserModel.query.filter_by(username=user_name).first()
    if passwordChangeForm.validate_on_submit() and logged_in:
        new_password = request.form['newPassword']
        user.setPassword(new_password)
        db.session.commit()
        return redirect(url_for('my_trivia'))
    return render_template('change_password.html', passwordChangeForm=passwordChangeForm, logged_in=logged_in, user_name=user_name)


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


def get_question_from_api(category=''):
    categories = [
        'artliterature',
        'language',
        'sciencenature',
        'general',
        'fooddrink',
        'peopleplaces',
        'geography',
        'historyholidays',
        'entertainment',
        'toysgames',
        'music',
        'mathematics',
        'religionmythology',
        'sportsleisure'
    ]
    api_url = f'https://api.api-ninjas.com/v1/trivia?category={category}'
    response = requests.get(api_url, headers={'X-Api-Key': 'IF8SxeQZrS0hn1pl7fSbHxvK5uscG5dhPFQVlsyI'})
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        flash('An error occurred.', 'alert-danger')
        return response.status_code, response.text


# Run the application if this script is being run directly
if __name__ == '__main__':
    # The host is set to '0.0.0.0' to make the app accessible from any IP address.
    # The default port is 5000.
    app.run(host='0.0.0.0', debug='true', port=5001)  # Default flask port (5000) is now used by macOS for sharing features
