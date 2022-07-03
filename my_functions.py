import pymongo
import requests
from datetime import timezone
import datetime
import os

mongo_db_password = os.environ['MONGO_DB_PW']

def cached_request(url, ttl):
    client = pymongo.MongoClient(f"mongodb+srv://travis:{mongo_db_password}@cluster0.ofivo.mongodb.net/?retryWrites=true&w=majority")

    db = client.requests
    collection = db.collection
    
    cache_result = collection.find_one({
        'url': url,
        'timestamp':{
            '$gt': datetime.datetime.now(timezone.utc) - datetime.timedelta(seconds=ttl)
        }
    })
    if cache_result:
        return cache_result
    else:
        return request_and_store(url, client)

def request_and_store(url, client):
    dt = datetime.datetime.now(timezone.utc)
    response_object = {
        'url': url,
        'timestamp': dt
    }

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