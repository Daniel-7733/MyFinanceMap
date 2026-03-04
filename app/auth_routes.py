"""
                            register/login/logout Codes

                            Make another blueprint for auth:
                            -> auth blueprint (login/register/logout)
                            (Like "main blueprint (transactions + dashboard)" in rout.py)

"""
from flask import Blueprint, render_template

auth: Blueprint = Blueprint("auth", __name__)


@auth.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    return render_template("sign_in.html", show_navbar=False)


@auth.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", show_navbar=False)


@auth.route("/log-out")
def log_out():
    return render_template("logout.html", show_navbar=False)

@auth.route("/user_form")
def user_form():
    return render_template("user_form.html", show_navbar=False)