from flask import render_template, request, redirect, url_for
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/login', methods=['POST'])
def login():
    # to-do: handle login later
    print("Login submitted")
    return redirect(url_for('index'))# assume logged in successfully


@app.route('/signup', methods=['POST'])
def signup():
    # to-do: handle sign up later
    print("Signup submitted")
    return redirect(url_for('auth', mode='signup'))


@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')