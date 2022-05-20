from flask import Flask, render_template, jsonify
import requests
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

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

        delta = timedelta(minutes=10)
        try:
            cutoff = datetime.utcnow() - delta
            mtime = datetime.utcfromtimestamp(os.path.getmtime('news.json'))
            if mtime < cutoff:
                try:
                    news_data = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}').json()
                    if news_data.get('code', '') == 'rateLimited':
                        with open('news.json', 'r') as f:
                            news_data = json.load(f)

                except:
                    return "an error occured"

                with open('news.json', 'w') as f:
                    json.dump(news_data, f)
            else:
                with open('news.json', 'r') as f:
                    news_data = json.load(f)
        except:
            try:
                news_data = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}').json()
                if news_data['code'] == 'rateLimited':
                    with open('news.json', 'r') as f:
                        news_data = json.load(f)
            except:
                return "an error occured"
            print(news_data)
            with open('news.json', 'w') as f:
                json.dump(news_data, f)

        return news_data


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

@app.route('/pollen')
def pollen():
    delta = timedelta(hours=6)
    try:
        cutoff = datetime.utcnow() - delta
        mtime = datetime.utcfromtimestamp(os.path.getmtime('pollen.json'))
        if mtime < cutoff:
            pollen_data = scrape_pollen()    
            with open('pollen.json', 'w') as f:
                json.dump(pollen_data, f)
        else:
            with open('pollen.json', 'r') as f:
                pollen_data = json.load(f)
    except:
        pollen_data = scrape_pollen()
        print(pollen_data)
        with open('pollen.json', 'w') as f:
            json.dump(pollen_data, f)

    # return jsonify([
    #     {'factor':'Test1', 'value':1000, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test2', 'value':900, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test3', 'value':800, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test4', 'value':700, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test5', 'value':600, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test6', 'value':500, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test7', 'value':400, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test8', 'value':300, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test9', 'value':200, 'fillColor':'#FFFFFF'},
    #     {'factor':'Test10', 'value':100, 'fillColor':'#FFFFFF'},
    # ])
    return jsonify(pollen_data)

def scrape_pollen():
    def find_json_text(text):
        started = False
        bracket_counts = defaultdict(int)
        for (i, c) in enumerate(text):
            if not started and c in '()[]{}':
                started = True
            if started:
                for bracket in [
                    {'open':'(', 'close':')', 'name':'parenthesis'},
                    {'open':'[', 'close':']', 'name':'parenthesis'},
                    {'open':'{', 'close':'}', 'name':'parenthesis'},
                ]:
                    if c == bracket['open']:
                        bracket_counts[bracket['name']] += 1
                    if c == bracket['close']:
                        bracket_counts[bracket['name']] -= 1
                        if bracket_counts[bracket['name']] < 0:
                            raise Exception('Unexpected closing bracket')
                if sum(bracket_counts.values()) == 0:
                    return text[:i]
        return ''

    def parse_factor(text):
        factor_names = {
            'Indoor Dust, Dander':'Dust/Dander'
        }
        first_quote_idx = text.find("'")
        second_quote_idx = text[first_quote_idx+1:].find("'") + first_quote_idx + 1
        factor = text[first_quote_idx+1:second_quote_idx]
        if factor in factor_names:
            factor = factor_names[factor]
        value = text[second_quote_idx+1:].split(',')[1]
        fill_color = re.search('#[0-9A-F]*', text[text.find('fill-color'):]).group(0)
        return {'factor':factor, 'value':int(value), 'fillColor':fill_color}

    response = requests.get('https://austinpollen.com/')
    pattern = r'(?<=<script defer>)(.*)(?=</script>)'
    script_text = re.findall(pattern, response.text, flags=re.DOTALL)[0]
    pattern = r'(?<=function drawChartindex\(\))(.*)(?<=arrayToDataTable\()(.*)'
    text = find_json_text(re.findall(pattern, script_text, flags=re.DOTALL)[0][0]).split('\n')

    return [parse_factor(x) for x in text[1:] if x.startswith('            [') and not x.startswith("            ['Factor'")]


if __name__ == "__main__":
    debug = True
    app.run(debug=True)