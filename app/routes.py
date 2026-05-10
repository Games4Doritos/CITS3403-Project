from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from app.forms import LoginForm, SignupForm
from app.models import Account, Profile

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
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
                return redirect(url_for("auth"))
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
                        return redirect(url_for("profile", mode="edit"))
                    # For existing user with profile
                    return redirect(url_for("profile"))
                
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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/leaderboard')
def leaderboard():
    from app.models import BestStats
    # Get top 10 scores ordered by highscore (highest first)
    top_scores = BestStats.query.order_by(BestStats.highscore.desc()).limit(10).all()
    return render_template('leaderboard.html', top_scores=top_scores)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    mode = request.args.get('mode', 'view')

    # Save profile form
    if request.method == 'POST':
        username = request.form.get('username')

        if username:
            # New user without a profile yet
            if not current_user.profile:
                profile = Profile(id=current_user.id, username=username)
                db.session.add(profile)

            # Existing user updating username
            else:
                current_user.profile.username = username

            db.session.commit()
            flash("Profile updated successfully.")
            return redirect(url_for("profile"))

    # New logged-in users must create profile first
    if not current_user.profile and mode != 'edit':
        return redirect(url_for("profile", mode="edit"))

    return render_template('profile.html', mode=mode)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404