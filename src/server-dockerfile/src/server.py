import flask
import json
import pymongo
import os
import datetime
import random


MAX_URL_LENGTH = 5
MAX_NUMBER = pow(62, MAX_URL_LENGTH)
DATABASE_COLLECTION = None

SERVER_PORT = None
DATABASE_URL = None
DATABASE_USERNAME = os.getenv('USERNAME', '')
DATABASE_PASSWORD = os.getenv('PASSWORD', '')
EXPIRATION_TIME = None


app = flask.Flask(__name__)


def readConfig():
    global SERVER_PORT
    global DATABASE_URL
    global EXPIRATION_TIME

    try:
        file = open('./config.json')
        data = json.load(file)
        SERVER_PORT = data['server_port']
        DATABASE_URL = data['database_url']
        EXPIRATION_TIME = data['expiration_time']
        
        file.close()
    except Exception as exception:
        print(exception)


def connectToDatabase():
    global DATABASE_COLLECTION
    try:
        auth = ''
        if DATABASE_USERNAME != '' and DATABASE_PASSWORD != '':
            auth = DATABASE_USERNAME + ':' + DATABASE_PASSWORD + '@'
        mongoClient = pymongo.MongoClient('mongodb://' + auth + DATABASE_URL)
        database = mongoClient["shorturl"]
        DATABASE_COLLECTION = database["url"]
        DATABASE_COLLECTION.drop_index('expiration_index')
        DATABASE_COLLECTION.create_index('created_at', expireAfterSeconds=EXPIRATION_TIME, name='expiration_index')
    except Exception as e:
        print(e)
        exit(-1)


def base10To62(number):
    base62 = ''

    if number == 0:
        return '0'

    while number != 0:
        remainder = number % 62
        if remainder <= 9:
            base62 = str(remainder) + base62
        elif 9 < remainder <= 35:
            base62 = chr(ord('A') + remainder - 10) + base62
        else:
            base62 = chr(ord('a') + remainder - 10 - 26) + base62

        number = number // 62
    return base62


def encodeToBase62(number):
    base62 = base10To62(number)
    if len(base62) < MAX_URL_LENGTH:
        base62 = ('0' * (MAX_URL_LENGTH - len(base62))) + base62
    return base62


def getShortURL(URL):
    entry = DATABASE_COLLECTION.find_one({'url': URL})
    return None if entry is None else entry['short_url']


def getURL(shortURL):
    entry = DATABASE_COLLECTION.find_one({'short_url': shortURL})
    return None if entry is None else entry['url']


def insertURL(URL):
    try:
        baseIndex = random.randrange(0, MAX_NUMBER)
        index = baseIndex
        if DATABASE_COLLECTION.count_documents({}) > MAX_NUMBER - 10000:
            return 'None'
        while True:
            entry = DATABASE_COLLECTION.find_one({'_id': index})
            if entry is None:
                break
            index = (index + 1) % MAX_NUMBER
            if index == baseIndex:
                return 'None'
        shortURL = encodeToBase62(index)
        entry = {
            '_id': index,
            'url': URL,
            'short_url': shortURL,
            'created_at': datetime.datetime.utcnow()
        }
        DATABASE_COLLECTION.insert_one(entry)
        return shortURL
    except Exception as e:
        print(e)


@app.route('/shorten/<string:URL>', methods=['POST'])
def shorten(URL):
    response = {}
    shortURL = getShortURL(URL)
    if shortURL is None:
        shortURL = insertURL(URL)
        if shortURL is None:
            response = {'short_url': str(shortURL)}
        else:
            response = {'short_url': flask.request.host_url + shortURL}
    else:
        DATABASE_COLLECTION.update_one({'short_url': shortURL}, {'$set': {'created_at': datetime.datetime.utcnow()}})
        response = {'short_url': flask.request.host_url + shortURL}

    return flask.jsonify(response)


@app.route('/<string:shortURL>', methods=['GET'])
def get(shortURL):
    entry = DATABASE_COLLECTION.find_one({'short_url': shortURL})
    URL = getURL(shortURL)
    response = {'url': str(URL)}
    return flask.jsonify(response)


if __name__ == '__main__':
    readConfig()
    connectToDatabase()
    app.run(host='0.0.0.0', port=SERVER_PORT)
