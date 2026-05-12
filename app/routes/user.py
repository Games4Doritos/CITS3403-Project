from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required

from app import db
from app.models import Account, Profile


user = Blueprint("user", __name__)


@user.route('/profile', methods=['GET', 'POST'])
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
            return redirect(url_for("user.profile", mode="edit"))
        # Check if another account already uses this email
        existing_account = Account.query.filter_by(email=email).first()
        # Prevent duplicate emails between users
        if existing_account and existing_account.id != current_user.id:
            flash("Email already in use.")
            return redirect(url_for("user.profile", mode="edit"))
            
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
        return redirect(url_for("user.profile"))

    # New logged-in users must create profile first
    if not current_user.profile and mode != 'edit':
        return redirect(url_for("user.profile", mode="edit"))

    return render_template('profile.html', mode=mode)