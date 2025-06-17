from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# Simple in-memory user store for demonstration
USERS = {
    "username": generate_password_hash("password")
}

def login(flask_app):
    @flask_app.route("/login", methods=["GET", "POST"])
    def login_view():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if username in USERS and check_password_hash(USERS[username], password):
                session["user"] = username
                return redirect(url_for("flask_index"))
            else:
                return render_template("login.html", error="Invalid username or password")
        return render_template("login.html")

    @flask_app.route("/logout")
    def logout_view():
        session.pop("user", None)
        return redirect(url_for("login_view"))

    @flask_app.route("/signup", methods=["GET", "POST"])
    def signup_view():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if not username or not password:
                return render_template("signup.html", error="Username and password required")
            if username in USERS:
                return render_template("signup.html", error="Username already exists")
            USERS[username] = generate_password_hash(password)
            return redirect(url_for("login_view"))
        return render_template("signup.html")
