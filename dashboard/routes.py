from flask import render_template, redirect, flash, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from dashboard.models import User, Device, Data, Dam
from dashboard import app, bcrypt, db, login_manager
from PIL import Image
from dashboard.forms import *
from dashboard.utility import *
import os
import pyttsx3
import time
import datetime
import json
import requests
import secrets



@app.route("/", methods=['GET', 'POST'])
@login_required
def dashboard():
    if len(current_user.works_at.devices) == 0:
        cur_level = 0
    else:
        cur_level = get_current_level()

    cur_status = determine_status(cur_level)
    if cur_status != current_user.works_at.status:
        inform_officials(cur_status, cur_level)
        current_user.works_at.status = cur_status
        db.session.commit()
    cur_weather = get_cur_weather()
    past_values = get_past_values()
    return render_template("dashboard.html", cur_level=cur_level, cur_weather=cur_weather, data=past_values)


@login_required
@app.route("/informPublic/", methods=['GET', 'POST'])
def inform_public():
    sms_form = SMSForm()
    twitter_form = TwitterForm()
    email_form = EmailForm()

    if sms_form.submit_sms.data and sms_form.validate():
        if inform_public_sms(sms_form.message_sms.data) and inform_public_telegram(sms_form.message_sms.data):
            return(redirect(url_for('inform_public')))

    elif twitter_form.submit_twitter.data and twitter_form.validate():
        if send_tweet(twitter_form.message_twitter.data):
            return (redirect(url_for('inform_public')))

    elif email_form.submit_email.data and email_form.validate():
        if send_email_authority(email_form.subject_email.data, email_form.message_email.data):
            return (redirect(url_for('inform_public')))


    return render_template('public-inform.html',
                           sms_form=sms_form,
                           twitter_form=twitter_form,
                           email_form=email_form)


@app.route("/addDevice/", methods=['GET', 'POST'])
@login_required
def add_device():
    form = DeviceForm()
    if form.validate_on_submit():
        api_key = secrets.token_urlsafe(32)
        hashed_key = bcrypt.generate_password_hash(api_key)
        device = Device(name=form.name.data,
                        mac=form.mac.data,
                        data_measured=form.data_measured.data,
                        api_key=hashed_key,
                        dam_id=current_user.works_at.id)
        db.session.add(device)
        db.session.commit()

        flash(f"API Key: {api_key}, Device Id: {device.id}", 'flash_success')

    return render_template("device.html", form=form)


@app.route("/sendFeed/", methods=["POST"])
def receive_feed():
    file = request.files['image']
    img = Image.open(file.stream)
    picture_fn = 'feed.png'
    picture_path = os.path.join(app.root_path, 'static/camera', picture_fn)
    img.save(picture_path)

    return jsonify({'success': True, })


@app.route("/register/", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        dam = Dam.query.filter_by(name=form.dam.data).first()
        user = User(username=form.username.data, password=hashed_password, dam_id=dam.id)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created. You can now login", 'flash_success')

    return render_template("register.html", form=form)


@app.route("/login/", methods=['GET', 'POST'])
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

