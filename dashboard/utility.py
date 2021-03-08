from dashboard.models import User, Device, Data, Dam
from dashboard import app, bcrypt, db
from dashboard.conf import *
from flask_login import current_user
from twilio.rest import Client
from twython import Twython
import time
import pyttsx3
import datetime
import json
import requests
import secrets

phone_numbers = ['+919871116254', '+919871624028']

def get_current_level():
    devices = current_user.works_at.devices
    cur_level = 0
    num_devices = 0
    for device in devices:
        if 'WATER LEVEL' in device.data_measured.upper():
            num_devices += 1
            water_data = Data.query.filter_by(device_id=device.id).all()
            if len(water_data):
                cur_level += water_data[-1].data

    return int(cur_level / num_devices)


def get_cur_weather():
    api_key = WEATHER_KEY
    lat = current_user.works_at.latitude
    lon = current_user.works_at.longitude
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"

    response = requests.get(url)

    weather_data = json.loads(response.text)
    weather_widget_data = {}
    if response.status_code == 200:
        weather_widget_data['temp'] = int(weather_data['main']['temp'] - 273.15)
        weather_widget_data['humidity'] = int(weather_data['main']['humidity'])
        weather_widget_data['visibility'] = int(weather_data['visibility'])
        weather_widget_data['title'] = weather_data['weather'][0]['main']
        weather_widget_data['icon'] = weather_data['weather'][0]['icon']
        print("Weather API call:", response.status_code)

    return weather_widget_data


def get_past_values():
    start_time = datetime.datetime.now() - datetime.timedelta(hours=2)
    rows = db.session.query(Data).filter(Data.timestamp > start_time).all()

    data = {}
    dam_devices = []
    for device in current_user.works_at.devices:
        data[device.id] = {'data': [], 'timestamps': []}
        dam_devices.append(device.id)

    for row in rows:
        device = row.device_id
        if device in dam_devices:
            data[device]['data'].append(row.data)
            data[device]['timestamps'].append(row.timestamp.strftime('%H:%M:%S'))

    return data


def determine_status(cur_level):
    percent_full = cur_level * 100 / current_user.works_at.frl

    if percent_full < 50:
        cur_status = 'NORMAL'

    elif percent_full < 75:
        cur_status = 'YELLOW'

    elif percent_full < 90:
        cur_status = 'ORANGE'

    else:
        cur_status = 'RED'

    return cur_status

def inform_officials(status, cur_level=0, num_persons=0):
    try:
        url = f'https://api.telegram.org/{BOT_ID}/sendMessage'

        if num_persons > 0:
            message = f'''{status} ALERT
Current Water Level: {cur_level}
Dam is {int(cur_level * 100 / current_user.works_at.frl)}% full
{num_persons} people spotted near the dam!'''

        else:
            message = f'''{status} ALERT
Current Water Level: {cur_level}
Dam is {int(cur_level * 100 / current_user.works_at.frl)}% full'''

        data = {"chat_id": OFFICIALS_CHAT_ID,
                "text": message}

        response = requests.post(url, params=data)
        if json.loads(response.text)["ok"]:
            print("Message sent to officials.")
    except Exception as e:
        print(e)
        print("Message not sent. Some problem occurred!")


def inform_public_telegram(message):
    try:
        url = f'https://api.telegram.org/{BOT_ID}/sendMessage'

        data = {"chat_id": PUBLIC_CHAT_ID,
                "text": message}

        response = requests.post(url, params=data)
        if json.loads(response.text)["ok"]:
            print("Telegram message sent to Public.")
        return True

    except Exception as e:
        print(e)
        print("Telegram message not sent. Some problem occurred!")
        return False

def inform_public_sms(message):
    client = Client(TWILIO_ACC_SID, TWILIO_AUTH_TOKEN)
    try:
        for number in phone_numbers:
            message = client.messages.create(
                messaging_service_sid=TWILIO_SERVICE_SID,
                body=message,
                to=number
            )
        print("SMS sent to Public.")
        return True

    except Exception as e:
        print("SMS not sent. Some error occurred!")
        print(e)
        return False


def send_email_authority(subject, message):
    url = f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages'

    data = {"from": f"{current_user.works_at.name} <mailgun@{MAILGUN_DOMAIN}>",
            "to": ["tejpunjraju8a@gmail.com", "sohangchopra@gmail.com"],
            "subject": subject,
            "text": message}

    response = requests.post(url, auth=("api", MAILGUN_API_KEY), data= data)

    print(response.text)
    if response.status_code == 200:
        print("Email sent")
        return True

    print(response.text)
    return False


def send_tweet(message):
    twitter = Twython(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    try:
        response = twitter.update_status(status=message)
        print(f"Tweet sent: Tweet ID: {response['id_str']} Created at: {response['created_at']}")
        return True

    except Exception as e:
        print("Tweet not sent. Some error occurred!")
        print(e)
        return False


def voice_alert(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()
    time.sleep(5)
    engine.stop()
    print("Here")





