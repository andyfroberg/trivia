#!/usr/local/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from forms import LoginForm, RegisterForm, PasswordChangeForm, TriviaAnswerForm, UserFilterForm
# from flask_login import login_user, logout_user, login_required, current_user
import flask_login
from models import db, login_manager, UserModel, TriviaQuestionModel, load_user #####
from datetime import datetime
# import requests
import json
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Create a new Flask application instance
app = Flask(__name__)

# Secret key (used for Flask sessions)
app.secret_key = os.getenv("FLASK_APP_SECRET_KEY")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trivia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
with app.app_context():
    db.create_all()
    questions = {}
    try:
        with open("general_easy_first50.json") as f:
            questions = json.load(f)
    except IOError as e:
        flash("There was an issue loading the database values.", "alert-danger")
        exit(1)

    for q in questions["results"]:
        question = TriviaQuestionModel()
        question.category = q["category"]
        question.difficulty = q["difficulty"]
        question.question = q["question"]
        question.correct_answer = q["correct_answer"]
        db.session.add(question)
        db.session.commit()

##### HELPER FUNCTIONS ########
def addUser(email, username, password):
    user = UserModel()
    user.set_password(password)
    user.email = email
    user.username = username
    user.score_current_round = 0
    user.score_lifetime = 0
    db.session.add(user)
    db.session.commit()

def verify_user_logged_in():
    logged_in = False
    username = None
    if flask_login.current_user.is_authenticated:
        logged_in = True
        username = flask_login.current_user.username
    return logged_in, username

@login_manager.unauthorized_handler
def handle_unauthorized_login_attempt():
    form = LoginForm()
    flash('Please login to access this page', 'alert-danger')
    return render_template('login.html',form=form)

def get_trivia_question(question_id=1, category='General Knowledge', 
                        type='multiple', difficulty='easy'):
    return TriviaQuestionModel.query.get(question_id)

def get_user_score_current_round():
    load_user()

def get_user_score_lifetime():
    pass

def get_user_profile():
    pass

# Initialize the login manager
login_manager.init_app(app)

def validate_form(method, form):
    return request.method == "POST" and not form.validate_on_submit()

############ ROUTES ###########
@app.route('/')
def home():
    logged_in, username = verify_user_logged_in()
    return render_template('home.html', logged_in=logged_in, username=username)

@app.route('/login', methods=['GET', 'POST'])
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
        if not user.check_password(form.password.data):
            flash('Please enter a valid password', 'alert-danger')
            return render_template('login.html',form=form)
        flask_login.login_user(user)
        session['email'] = form.email.data
        return redirect(url_for('my_trivia', order_by_date=0))
    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    flask_login.logout_user()
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/register', methods=["GET", "POST"])
def register():
    logged_in, username = verify_user_logged_in()
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
                flask_login.login_user(user)
                return redirect(url_for('my_trivia', order_by_date=0))  # may need to go back to 'login' if still buggy
            else:
                flash('Passwords do not match', 'alert-danger')
                return render_template('register.html',form=form)
        else:
            flash('Email already registered', 'alert-danger')
            return render_template('register.html',form=form)    
    return render_template('register.html',form=form, logged_in=logged_in, username=username)

@app.route('/my-trivia', methods=['GET', 'POST'])
def my_trivia():
    answer_form = TriviaAnswerForm()
    logged_in = False
    username = None
    if flask_login.current_user.is_authenticated:
        logged_in = True
        username = flask_login.current_user.username  #???
        score = flask_login.current_user.score_current_round  #???
        question = get_trivia_question()
        if answer_form.validate_on_submit():  
            if request.form['answer'].lower() == question.correct_answer.lower():
                flask_login.current_user.score_current_round += 1
                db.session.commit()
                flash('Your answer is correct!', 'alert-success')
            else:
                flash(f"Your answer is incorrect. The correct answer was {question.correct_answer}", 'alert-danger')
        user_score = flask_login.current_user.score_current_round
        return render_template('my-trivia.html', answer_form=answer_form, logged_in=logged_in, 
                               username=username, question=question, user_score=user_score)
    return render_template("login.html")

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    user_filter_form = UserFilterForm()
    users = UserModel.query.all()
    logged_in, username = verify_user_logged_in()
    # Check if the user has searched for an event by title
    if user_filter_form.validate_on_submit():
        filtered_users = []
        for user in users:
            if request.form['query'].lower() in str(user.username).lower():
                filtered_users.append(user)
            users = filtered_users
        return render_template('leaderboard.html', user_filter_form=user_filter_form, users=users, 
                               logged_in=logged_in, username=username)
    return render_template('leaderboard.html', user_filter_form=user_filter_form, users=users, 
                           logged_in=logged_in, username=username)

@app.route('/change_password', methods=["GET", "POST"])
def change_password():
    passwordChangeForm = PasswordChangeForm()
    if flask_login.current_user.is_authenticated:
        logged_in = True
        username = flask_login.current_user.username
        user = UserModel.query.filter_by(username=username).first()
    if passwordChangeForm.validate_on_submit() and logged_in:
        new_password = request.form['newPassword']
        user.set_password(new_password)
        db.session.commit()
        return redirect(url_for('reminders', order_by_date=0))
    return render_template('change_password.html', passwordChangeForm=passwordChangeForm, logged_in=logged_in, username=username)


####### ERROR PAGES ###########
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    # Default flask port (5000) is used in newer macOS releases for sharing features.
    app.run(host='0.0.0.0', debug='false', port=5001)  
