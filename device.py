from time import sleep
from datetime import datetime
from random import randrange
import requests


while True:
    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    data = randrange(0,200)
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    to_send =  {'api_key': api_key, 'data': data, 'timestamp': time}

    response = requests.put('http://127.0.0.1:5000/update/1/',data=to_send)

    print(response.status_code)
    sleep(30)
