from flask import Blueprint, render_template, redirect, url_for, session, flash
from recipe.adapters.memory_repo import MemoryRepository
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from functools import wraps
import recipe.authentication.auth_services as auth_services

authentication_bp = Blueprint('authentication', __name__)
repo = MemoryRepository()


def logout_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_name' in session:
            return redirect(url_for('home.home'))
        return view(**kwargs)
    return wrapped_view


@authentication_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    form = RegistrationForm()
    register_error_message = None

    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        try:
            auth_services.add_user(user_name, password, repo)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('authentication.login'))
        except auth_services.NameNotUniqueException:
            register_error_message = "Username is already taken."
        except Exception as e:
            register_error_message = "Registration failed. Please try again."

    return render_template(
        'credentials.html',
        form=form,
        title='Register',
        handler_url=url_for('authentication.register'),
        register_error_message=register_error_message
    )


@authentication_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    login_error_message = None

    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        try:
            auth_services.authenticate_user(user_name, password, repo)
            session.clear()
            session['user_name'] = user_name
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home.home'))
        except auth_services.UnknownUserException:
            login_error_message = "Unknown username."
        except auth_services.AuthenticationException:
            login_error_message = "Incorrect username or password."
        except Exception as e:
            login_error_message = "Login failed. Please try again."

    return render_template(
        'credentials.html',
        form=form,
        title='Login',
        handler_url=url_for('authentication.login'),
        login_error_message=login_error_message
    )


@authentication_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home.home'))


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_name' not in session:
            return redirect(url_for('authentication.login'))
        return view(**kwargs)
    return wrapped_view


class RegistrationForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired(message='Username is required')])
    password = PasswordField('Password', validators=[DataRequired(message='Password is required')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired(message='Username is required')])
    password = PasswordField('Password', validators=[DataRequired(message='Password is required')])
    submit = SubmitField('Login')
