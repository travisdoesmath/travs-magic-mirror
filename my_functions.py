from pymongo import MongoClient
import requests
from datetime import timezone
import datetime

def cached_request(url, ttl):
    client = MongoClient()
    db = client.requests
    collection = db.collection
    
    cache_result = collection.find_one({
        'timestamp':{
            'url': url,
            '$gt': datetime.datetime.now(timezone.utc) - datetime.timedelta(seconds=ttl)
        }
    })
    if cache_result:
        return cache_result
    else:
        return request_and_store(url)

def request_and_store(url):
    dt = datetime.datetime.now(timezone.utc)
    response_object = {
        'url': url,
        'timestamp': dt
    }

    client = MongoClient()
    db = client.requests
    collection = db.collection

    try:
        response = requests.get(url)
        response_object['status'] = response.status_code
        response_object['content'] = response.content
        collection.insert_one(response_object)
    except requests.exceptions.RequestException as e:
        response_object['status'] = 0
        response_object['content'] = e
        collection.insert_one(response_object)
    return response_object