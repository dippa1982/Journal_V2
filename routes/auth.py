from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models.user import User

auth_bp = Blueprint(
    "auth",
    __name__
)

from extensions import db, login_manager
#--------------------------------
# LOGIN
#--------------------------------
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")

#--------------------------------
# LOGOUT
#--------------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

#--------------------------------
# REGISTER
#--------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("That username already exists.")
            return redirect(url_for("auth.register"))

        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for("dashboard.dashboard"))

    return render_template("register.html")

#--------------------------------
# LOGIN MANAGER
#--------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))