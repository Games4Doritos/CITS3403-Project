from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from json import loads

from app import app, db
from app.forms import LoginForm, SignupForm
from app.models import Account, Profile, BestStats

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

@app.route('/play', methods=["GET", "POST"])
def play():
    
    def validateResults(requestData):
        #checks if any of the figures are negative (invalid)
        if requestData["totalJumps"] < 0:
            return False
        
        if requestData["newCurrency"] < 0:
            return False
            
        if requestData["finalTime"] < 0:
            return False

        if requestData["totalScore"] < 0:
            return False
        
        #checks if total score < time (invalid as score += 100*deltaTime (s) at each frame)
        if requestData["totalScore"] < requestData["finalTime"]:
            return False
        #checks if the score is possible within the given time
        #total score before max multiplier: 100(20*1.5 + 20*1.6 +...+ 20*5.4) = 276000 (happens over 800 seconds)
        #includes baseMultiplier progression and assumes the player is holding jump for the entire time (hence start at 1.5)
        intervalCount = int(requestData["finalTime"])//20
        maxPossibleScore = 0
        if intervalCount <= 40:
            for i in range(intervalCount):
                maxPossibleScore += 20 * (1.5 + 0.1*i)
            maxPossibleScore += (requestData["finalTime"] - 20*intervalCount)*(1.5+0.1*intervalCount)
            maxPossibleScore *= 100
        else:
            maxMultiplierTime = requestData["finalTime"] - 800
            maxPossibleScore = 100*(5.5 * maxMultiplierTime + 2760)
        if maxPossibleScore < requestData["totalScore"]:
            return False

        return True
    
    if request.method == "POST":
        
        requestData = loads(request.data.decode())
        #checks that the user submitting the run is logged in
        if current_user.is_authenticated:
            #basic server-side validation for results
            valid = validateResults(requestData)
            if not valid:
                return "Invalid Run Results", 400
            if not current_user.best_stats:
                #creates a new BestStats object and links it to the user for future uploads
                bestStats = BestStats(id=current_user.id, 
                                    highscore=requestData["totalScore"],
                                    longest_time=requestData["finalTime"],
                                    jump_count=requestData["totalJumps"],
                                    currency=requestData["newCurrency"],
                                    total_games=1
                                    )
                db.session.add(bestStats)
                db.session.commit()
            else:
                curBestStats = current_user.best_stats
                
                #one final validation for types
                if curBestStats.highscore < requestData["totalScore"]:
                    current_user.best_stats.highscore = round(requestData["totalScore"])
                    
                if curBestStats.longest_time < requestData["finalTime"]:
                    current_user.best_stats.longest_time = requestData["finalTime"]
                    
                current_user.best_stats.currency += int(requestData["newCurrency"])
                current_user.best_stats.jump_count += int(requestData["totalJumps"])
                db.session.commit()
                    
            
            return "Run Successfully Submitted!", 200
        
    
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
        email = request.form.get('email')
        # Basic validation to prevent empty fields
        if not username or not email:
            flash("Username and email are required.")
            return redirect(url_for("profile", mode="edit"))
        # Check if another account already uses this email
        existing_account = Account.query.filter_by(email=email).first()
        # Prevent duplicate emails between users
        if existing_account and existing_account.id != current_user.id:
            flash("Email already in use.")
            return redirect(url_for("profile", mode="edit"))
            
        current_user.email = email
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