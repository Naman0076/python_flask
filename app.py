import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy.orm import Session
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from models.users import init_models, User, db
from dotenv import load_dotenv
import configure_logging 
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Load secret key from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')  # Load database URI from .env
logging.info("configuring flask secret key and SQL database")

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
init_models(app)

@login_manager.user_loader
def load_user(user_id):
    with Session(db.engine) as session:
        return session.get(User, int(user_id))

@app.route('/')
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html', title='Dashboard', username=current_user.username)
logging.info("requesting base endpoint")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('Logged in successfully!', 'success')
            logging.info("login successfull")
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            logging.error("login error invalid username or password")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
logging.info("requesting /logout endpoint")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
logging.info("requesting /register endpoint to register a new user")

if __name__ == '__main__':
    app.run(debug=True, port=8000)
logging.info("running the app")