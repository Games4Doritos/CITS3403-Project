from flask import render_template
from app import app

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route