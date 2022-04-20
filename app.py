from flask import Flask, render_template
import requests
import os

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
    try:
        response = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}').json()
        return response
    except:
        return "an error occured"

@app.route('/weather')
def weather():
    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={owm_api_key}&units=imperial').json()
        austin_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q=austin&appid={owm_api_key}&units=imperial').json()
        response['austin'] = austin_response
        return response
    except:
        return "an error occured"

@app.route('/austin-weather')
def austin_weather():
    lat = 30.2672
    lng = -97.7431
    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={owm_api_key}&units=imperial').json()
        return response
    except:
        return "an error occured"

if __name__ == "__main__":
    app.run(debug=True)