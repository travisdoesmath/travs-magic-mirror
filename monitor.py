from flask import Flask, render_template, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('monitor.html')

if __name__ == "__main__":
    debug = True
    app.run(debug=True)
