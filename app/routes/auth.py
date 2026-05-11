from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from app import db
from app.forms import LoginForm, SignupForm
from app.models import Account


auth = Blueprint("auth", __name__)

@auth.route("/auth", methods=["GET", "POST"])
def login_signup():
    login_form = LoginForm()
    signup_form = SignupForm()

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == "signup":
            if signup_form.validate_on_submit():
                account = Account(email=signup_form.email.data)
                account.set_password(signup_form.password.data)
                account.generate_friend_code()

                # Add new account to database
                db.session.add(account)
                db.session.commit()

                flash("Account created successfully. Please log in.", "signup_success")
                return redirect(url_for("auth.login_signup"))
            else:
                print(signup_form.errors)
                flash("Signed up failed", "signup_error")
                return render_template(
                    "auth.html",
                    login_form=login_form,
                    signup_form=signup_form,
                    mode="signup" # to still display signup form
                )

        if form_type == "login":
            if login_form.validate_on_submit():
                account = Account.query.filter_by(email=login_form.email.data).first()

                # Password hashes matches
                if account and account.check_password(login_form.password.data):
                    # Create login session
                    login_user(account)
                    
                    # For new signups that do not have profile
                    if not account.profile: 
                        return redirect(url_for("user.profile", mode="edit"))
                    # For existing user with profile
                    return redirect(url_for("user.profile"))
                
                # Password hashes does not match or No such account
                flash("Invalid email or password", "login_error")
                return render_template(
                    "auth.html",
                    login_form=login_form,
                    signup_form=signup_form,)
            else:
                print(login_form.errors)
                return render_template(
                    "auth.html",
                    login_form=login_form,
                    signup_form=signup_form,
                )

    return render_template(
        'auth.html',
        login_form=login_form,
        signup_form=signup_form
    )

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))