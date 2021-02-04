from flask import render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from dashboard.forms import RegistrationForm, LoginForm, DeviceForm
from dashboard.models import User, Device, Data, Dam
from dashboard import app, bcrypt, db, login_manager


@app.route("/", methods=['GET','POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/update/API_KEY=<api_key>/mac=<mac>/data=<data>")
def update(api_key, mac, data):
    return render_template("update.html", data=data)

@app.route("/register/", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        dam = dam = Dam.query.filter_by(name=form.dam.data).first()
        user = User(username=form.username.data, password=hashed_password, dam_id=dam.id)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created. You can now login", 'flash_success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login/", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash("Incorrect username or password", 'flash_fail')

    return render_template("login.html", form=form)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('login'))