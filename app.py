from flask import Flask, render_template
import requests
import json
import os

debug = False

news_api_key = os.environ['NEWS_API_KEY']
owm_api_key = os.environ['OWM_API_KEY']
lat = os.environ['MY_LATITUDE']
lng = os.environ['MY_LONGITUDE']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def news():
    if debug:
        print('news.json loaded for debugging')
        with open('news.json', 'r') as f:
            response = json.load(f)
            return response
    else:
        try:
            response = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}').json()
            return response
        except:
            return "an error occured"

@app.route('/weather')
def weather():
    if debug:
        print('weather.json loaded for debugging')
        with open('weather.json', 'r') as f:
            response = json.load(f)
            return response
    else:
        try:
            response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={owm_api_key}&units=imperial').json()
            return response
        except:
            return "an error occured"

if __name__ == "__main__":
    debug = True
    app.run(debug=True)