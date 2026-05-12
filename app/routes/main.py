from flask import Blueprint, render_template

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404