from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required

from app import db
from app.models import Profile
from app.forms import EditProfileForm


user = Blueprint("user", __name__)

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    mode = request.args.get('mode', 'view')

    # Create edit profile form
    form = EditProfileForm()

    # Handle profile form submission
    if request.method == 'POST':

        # Save profile form after validation
        if form.validate_on_submit():

            # Remove extra spaces from inputs
            username = form.username.data.strip()
            email = form.email.data.strip().lower()

            # Update account email
            current_user.email = email

            # New user without a profile yet
            if not current_user.profile:
                profile = Profile(id=current_user.id,username=username)
                db.session.add(profile)

            # Existing user updating username
            else:
                current_user.profile.username = username

            db.session.commit()

            flash("Profile updated successfully.")
            return redirect(url_for("user.profile"))

        # Display validation errors
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error)

            return redirect(url_for("user.profile", mode="edit"))

    # New logged-in users must create profile first
    if not current_user.profile and mode != 'edit':
        return redirect(url_for("user.profile", mode="edit"))

    return render_template('profile.html',mode=mode,form=form)