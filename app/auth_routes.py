"""
                            register/login/logout Codes

                            Make another blueprint for auth:
                            -> auth blueprint (login/register/logout)
                            (Like "main blueprint (transactions + dashboard)" in rout.py)

"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user


from .models import User, db
from .core.dates import get_full_current_date
from .core.security import verify_password
from .services.auth import parse_register_form


auth: Blueprint = Blueprint("auth", __name__)


@auth.route("/debug-users")
def debug_users():
    """For debugging purposes"""
    users = User.query.all()
    return {"count": len(users), "emails": [u.email for u in users]}


@auth.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        print("REGISTER POST HIT ✅")
        print("FORM:", dict(request.form))

        data = parse_register_form(request.form)
        print("PARSED DATA:", data)

        if data is None:
            print("REGISTER FAILED ❌ parse_register_form returned None")
            return render_template("sign_in.html", show_navbar=False, timezone=get_full_current_date())

        user = User(
            username=data.email,
            email=data.email,
            password_hash=data.password_hash,
            home_currency=data.home_currency,
            location=data.location,
        )
        db.session.add(user)
        db.session.commit()
        print("REGISTER SAVED ✅ user_id:", user.id)

        return redirect(url_for("auth.login"))

    return render_template("sign_in.html", show_navbar=False, timezone=get_full_current_date())

# @auth.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = (request.form.get("email") or "").strip().lower()
#         password = request.form.get("password") or ""
#
#         user = User.query.filter_by(email=email).first()
#
#         if user and verify_password(password, user.password_hash):
#             login_user(user)  # optionally: login_user(user, remember=True)
#             return redirect(url_for("main.home"))
#
#         flash("Invalid email or password", "error")
#
#     return render_template("login.html", show_navbar=False)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()

        print("LOGIN ATTEMPT:", email, "user_found=", bool(user))
        if user:
            print("HASH IN DB:", user.password_hash[:20], "...")

        ok = bool(user) and verify_password(password, user.password_hash)
        print("PASSWORD OK:", ok)

        if ok:
            login_user(user)
            print("AFTER login_user -> authenticated:", current_user.is_authenticated, "id:", current_user.get_id())
            return redirect(url_for("main.home"))

        flash("Invalid email or password", "error")

    return render_template("login.html", show_navbar=False)


@auth.route("/log-out")
@login_required
def log_out():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("auth.login"))

