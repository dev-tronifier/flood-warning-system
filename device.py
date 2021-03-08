from time import sleep
import datetime
import random
import requests


while True:
    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    data = random.randrange(0,200)
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    to_send =  {'api_key': api_key, 'data': data, 'timestamp': time}

    response = requests.put('http://127.0.0.1:5000/update/1/',data=to_send)

    print(response.status_code)
    sleep(30)

