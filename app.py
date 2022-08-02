from flask import Flask, render_template, jsonify
import requests
import json
import math
import os
import re
import urllib
from collections import defaultdict
from datetime import datetime, timedelta
from my_functions import cached_request

debug = False

news_api_key = os.environ['NEWS_API_KEY']
owm_api_key = os.environ['OWM_API_KEY']
bing_maps_key = os.environ['BING_MAPS_KEY']
lat = os.environ['MY_LATITUDE']
lng = os.environ['MY_LONGITUDE']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/v2')
def index_v2():
    return render_template('index_v2.html')

@app.route('/traffic')
def traffic():
    home_address = "8519 Cahill Dr, Austin, TX 78729"
    work_address = "3429 Executive Center Dr, Austin, TX"
    arwen_address = "134 World of Tennis Sq, Lakeway, TX"
    base_url = "https://dev.virtualearth.net/REST/V1/Routes/Driving?"

    params = {
        'wp.0':home_address,
        'wp.1':work_address,
        'key':bing_maps_key
    }

    urls = {
        'home_to_work': base_url + urllib.parse.urlencode({'wp.0':home_address, 'wp.1':work_address, 'key':bing_maps_key}),
        'work_to_home': base_url + urllib.parse.urlencode({'wp.0':work_address, 'wp.1':home_address, 'key':bing_maps_key}),

        'home_to_arwen': base_url + urllib.parse.urlencode({'wp.0':home_address, 'wp.1':arwen_address, 'key':bing_maps_key}),
        'arwen_to_home': base_url + urllib.parse.urlencode({'wp.0':arwen_address, 'wp.1':home_address, 'key':bing_maps_key}),

        'arwen_to_work': base_url + urllib.parse.urlencode({'wp.0':arwen_address, 'wp.1':work_address, 'key':bing_maps_key}),
        'work_to_arwen': base_url + urllib.parse.urlencode({'wp.0':work_address, 'wp.1':arwen_address, 'key':bing_maps_key}),
    }
        
    
    response = {key:cached_request(urls[key], 600) for key in urls}
    #debug = response['home_to_work']
    #print(debug)
    #print(json.loads(debug))
    #print(json.loads(debug['content']))
    time_to_work = math.ceil(json.loads(response['home_to_work']['content'])['resourceSets'][0]['resources'][0]['travelDurationTraffic']/60)
    time_to_arwen = math.ceil(json.loads(response['home_to_arwen']['content'])['resourceSets'][0]['resources'][0]['travelDurationTraffic']/60)
    return {
        'work': time_to_work,
        'arwen': time_to_arwen,
    }

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
    response = cached_request(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={owm_api_key}&units=imperial', 300)
    return json.loads(response['content'])

    # if debug:
    #     print('weather.json loaded for debugging')
    #     with open('weather.json', 'r') as f:
    #         response = json.load(f)
    #         return response
    # else:
    #     try:
    #         response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={owm_api_key}&units=imperial').json()
    #         return response
    #     except:
    #         return "an error occured"

@app.route('/pollen')
def pollen():
    delta = timedelta(hours=1)
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

    response_index = requests.get('https://austinpollen.com/')
    response_usualsuspects = requests.get('https://austinpollen.com/theusualsuspects.html')
    script_pattern = r'(?<=<script defer>)(.*)(?=</script>)'
    script_text_index = re.findall(script_pattern, response_index.text, flags=re.DOTALL)[0]
    script_text_usualsuspects = re.findall(script_pattern, response_usualsuspects.text, flags=re.DOTALL)[0]
    pattern_index = r'(?<=function drawChartindex\(\))(.*)(?<=arrayToDataTable\()(.*)'
    pattern_usualsuspects = r'(?<=function drawCharttheusualsuspects\(\))(.*)(?<=arrayToDataTable\()(.*)'
    text_index = find_json_text(re.findall(pattern_index, script_text_index, flags=re.DOTALL)[0][0]).split('\n')
    text_usualsuspects = find_json_text(re.findall(pattern_usualsuspects, script_text_usualsuspects, flags=re.DOTALL)[0][0]).split('\n')

    return [parse_factor(x) for x in text_index[1:] if x.startswith('            [\'Indoor Dust, Dander') and not x.startswith("            ['Factor'")] + [parse_factor(x) for x in text_usualsuspects[1:] if x.startswith('            [') and not x.startswith("            ['Factor'")]


if __name__ == "__main__":
    debug = True
    app.run(debug=True)