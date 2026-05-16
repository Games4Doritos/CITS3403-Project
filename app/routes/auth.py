from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required
from flask_mail import Message

from app import db, mail
from app.forms import LoginForm, SignupForm, RequestResetForm, ResetPasswordForm
from app.models import Account
from app.tokens import generate_token, confirm_token

auth = Blueprint("auth", __name__)

def send_email(to, subject, body):
    message = Message(
        subject=subject, 
        recipients=[to],
        body=body,
        sender=current_app.config["MAIL_USERNAME"]
    )
    mail.send(message)


@auth.route("/auth")
def auth_page():
    mode = request.args.get("mode")
    token = request.args.get("token")
    return render_template(
        "auth.html",
        login_form=LoginForm(),
        signup_form=SignupForm(),
        reset_request_form=RequestResetForm(),
        reset_password_form=ResetPasswordForm(),
        mode=mode,
        token=token
    )

@auth.route("/signup", methods=["POST"])
def signup():
    signup_form = SignupForm()

    if not signup_form.validate_on_submit():
        flash("Sign up failed", "signup_error")
        return redirect(url_for("auth.auth_page", mode="signup"))

    existing_account = Account.query.filter_by(
        email=signup_form.email.data
    ).first()

    if existing_account:
        flash("This email is already registered", "signup_error")
        return redirect(url_for("auth.auth_page", mode="signup"))

    account = Account(email=signup_form.email.data)
    account.set_password(signup_form.password.data)
    account.generate_friend_code()

    db.session.add(account)
    db.session.commit()

    session["pending_verification_email"] = account.email

    token = generate_token(account.email, "verify_email")

    verify_url = url_for(
        "auth.verify_email",
        token=token,
        _external=True
    )

    send_email(
        account.email,
        "Verify your email",
        f"Please verify your email using this link: {verify_url}"
    )

    flash(
        "Account created successfully. Please check your email to verify your account.",
        "verification_required"
    )

    return redirect(url_for("auth.auth_page", mode="resend-verification"))

@auth.route("/login", methods=["POST"])
def login():
    login_form = LoginForm()

    if not login_form.validate_on_submit():
        flash("Login failed", "login_error")
        return redirect(url_for("auth.auth_page"))

    account = Account.query.filter_by(email=login_form.email.data).first()

    if account and account.check_password(login_form.password.data):

        if not account.is_email_verified:
            session["pending_verification_email"] = account.email
            flash("Please verify your email before logging in.", "verification_required")
            return redirect(url_for("auth.auth_page", mode="resend-verification"))

        login_user(account)

        if not account.profile:
            return redirect(url_for("user.profile", mode="edit"))

        return redirect(url_for("user.profile"))

    flash("Invalid email or password", "login_error")
    return redirect(url_for("auth.auth_page"))

@auth.route("/verify-email/<token>")
def verify_email(token):
    email = confirm_token(token, "verify_email", 12 * 60 * 60)

    if email is None:
        flash("Verification link is invalid or expired.", "verification_fail")
        return redirect(url_for("auth.auth_page", mode="resend-verification"))

    account = Account.query.filter_by(email=email).first()

    if account is None:
        flash("Account not found", "signup_error")
        return redirect(url_for("auth.auth_page", mode="signup"))

    if account.is_email_verified:
        flash("Email is already verified. You can log in.", "verification_success")
        return redirect(url_for("auth.auth_page"))

    account.is_email_verified = True
    db.session.commit()

    session.pop("pending_verification_email", None)

    flash("Email verified. You can now log in.", "verification_success")
    return redirect(url_for("auth.auth_page"))

@auth.route("/resend-verification", methods=["POST"])
def resend_verification():

    email = session.get("pending_verification_email")

    if email is None:
        flash("No pending verification email found.", "verification_fail")
        return redirect(url_for("auth.auth_page", mode="signup"))

    account = Account.query.filter_by(email=email).first()

    if account is None:
        flash("Account not found.", "verification_fail")
        return redirect(url_for("auth.auth_page", mode="signup"))

    if account.is_email_verified:
        flash("Email is already verified. You can log in.", "verification_success")
        return redirect(url_for("auth.auth_page"))

    token = generate_token(account.email, "verify_email")

    verify_url = url_for(
        "auth.verify_email",
        token=token,
        _external=True
    )

    send_email(
        account.email,
        "Verify your email",
        f"Please verify your email using this link: {verify_url}"
    )

    flash(
        "Verification email resent. Please check your email.",
        "verification_required"
    )

    return redirect(url_for(
        "auth.auth_page",
        mode="resend-verification"
    ))

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    reset_request_form = RequestResetForm()

    if reset_request_form.validate_on_submit():

        account = Account.query.filter_by(email=reset_request_form.email.data).first()

        if account:
            token = generate_token(account.email, "password-reset")

            reset_link = url_for(
                "auth.reset_password",
                token=token,
                _external=True
            )

            body = f"To reset your password, visit: {reset_link} If you did not request this password reset, ignore this email."

            send_email(account.email, "Password Reset Request", body)

        flash(
            "If the email exists, a password reset link has been sent.",
            "reset_required"
        )

        return redirect(url_for("auth.auth_page"))

    return redirect(url_for("auth.auth_page", mode="forgot-password"))

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    email = confirm_token(token, "password-reset", max_age= 60 * 60)

    if email is None:
        flash("Invalid or expired reset link.", "reset_fail")

        return redirect(url_for("auth.auth_page", mode="forgot-password"))

    account = Account.query.filter_by(email=email).first()

    if account is None:
        flash("Account not found.", "reset_fail")

        return redirect(url_for("auth.auth_page"))

    reset_password_form = ResetPasswordForm()

    if request.method == "POST":
        if reset_password_form.validate_on_submit():

            account.set_password(reset_password_form.password.data)

            db.session.commit()

            flash("Password reset successful. You can now log in.", "reset_success")

            return redirect(url_for("auth.auth_page"))

    return redirect(url_for("auth.auth_page", mode="reset-password",token=token))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

