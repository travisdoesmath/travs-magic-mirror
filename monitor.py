from flask import Flask, render_template, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('monitor.html')


@app.route('/chromium')
def chromium():
    chromium_console = requests.get('http://localhost:9222')
    return chromium_console.text

if __name__ == "__main__":
    debug = True
    app.run(debug=True)
