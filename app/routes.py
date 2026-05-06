from flask import render_template, request, redirect, url_for, flash
from app import app
from app.forms import LoginForm, SignupForm

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
            if signup_form.validate():
                print("Signup valid")
                flash("Account created successfully. Please log in.")
                # To do later: save new player account
                return redirect(url_for("auth"))
            else:
                print(signup_form.errors)
                return render_template(
                    "auth.html",
                    login_form=login_form,
                    signup_form=signup_form,
                    mode="signup" # to still display signup form
                )

        if form_type == "login":
            if login_form.validate():
                print("Login valid")
                # To do later: log in player
                return redirect(url_for("index"))
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

@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/edit-profile')
def edit_profile():
    return render_template('edit_profile.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404