from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth = Blueprint('auth', __name__)

# Role constants
ADMIN_ROLE = "adminRole"
USER_ROLE = "userRole"

# Utility function for password validation
def is_password_strong(password):
    """Checks if the password meets minimum strength requirements."""
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )

@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        admin = User.query.filter_by(email=email, role=ADMIN_ROLE).first()

        if admin:
            if check_password_hash(admin.password, password):
                login_user(admin)
                flash("Admin login successful!", "success")
                return redirect(url_for('views.admin_dashboard'))
            else:
                flash("Invalid password.", "error")
        else:
            flash("No admin user found with that email.", "error")

    return render_template('admin_login.html')


@auth.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email, role=USER_ROLE).first()

        if not user:
            flash("No user found with that email.", "error")
            return redirect(url_for('auth.user_login'))

        if user.role == ADMIN_ROLE:
            flash("Admins should use the admin login page.", "warning")
            return redirect(url_for('auth.admin_login'))

        if check_password_hash(user.password, password):
            login_user(user)
            flash("User logged in successfully!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('views.user_dashboard'))
        else:
            flash("Invalid email or password.", "error")

    return render_template('user_login.html')


@auth.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Validate inputs
        if not name or not email or not password or not role:
            flash("All fields are required.", "error")
            return redirect(url_for('auth.signup'))

        if role not in [ADMIN_ROLE, USER_ROLE]:
            flash("Invalid role selected.", "error")
            return redirect(url_for('auth.signup'))

        if not is_password_strong(password):
            flash("Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.", "error")
            return redirect(url_for('auth.signup'))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "error")
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(name=name, email=email, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()

            if role == ADMIN_ROLE:
                flash("Admin account created successfully! You can now log in.", "success")
                return redirect(url_for('auth.admin_login'))
            else:
                flash("User account created successfully! You can now log in.", "success")
                return redirect(url_for('auth.user_login'))

    return render_template('signup.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('views.home'))
