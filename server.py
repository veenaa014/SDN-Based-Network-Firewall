from flask import Flask
import threading

import pymongo
from pymongo import MongoClient


app = Flask(__name__)

client = MongoClient('3.92.107.201', 27017)
logdb = client.pox.log

@app.route('/')
def index():
    col = client.pox.rules
    return "Hello, World!" + str(col.find_one()['protocol'])

@app.route('/log')
def getlog():
    res = ""
    for entry in logdb.find(limit=40).sort("_id", pymongo.DESCENDING):
        res = res + "[" + entry['time'].strftime("%m/%d/%Y, %H:%M:%S.%f") + "] " + entry['message'] + "\n"
    return res


app.run(debug=False, port=80, host='0.0.0.0')
