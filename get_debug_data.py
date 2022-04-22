import requests
import os
import json

news_api_key = os.environ['NEWS_API_KEY']
owm_api_key = os.environ['OWM_API_KEY']
lat = os.environ['MY_LATITUDE']
lng = os.environ['MY_LONGITUDE']

news_response = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}').json()
weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={owm_api_key}&units=imperial').json()

with open('news.json', 'w') as f:
    json.dump(news_response, f)

with open('weather.json', 'w') as f:
    json.dump(weather_response, f)
