from flask import Flask
from flask import request, send_from_directory, redirect, url_for
import threading

import pymongo
from pymongo import MongoClient


app = Flask(__name__)

client = MongoClient('3.92.107.201', 27017)
logdb = client.pox.log
rules = client.pox.rules

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/gui/<path:path>')
def gui(path):
    return send_from_directory('frontend', path)

@app.route('/log')
def getlog():
    res = ""
    for entry in logdb.find(limit=40).sort("_id", pymongo.DESCENDING):
        res = res + "[" + entry['time'].strftime("%m/%d/%Y, %H:%M:%S.%f") + "];" + entry['message'] + "\n"
    return res

@app.route('/rules', methods=['GET'])
def getrules():
    res = ""
    for entry in rules.find():
        res = res + entry['protocol'] + ";" + entry['source'] + ";" + entry['destination'] + ";" + str(entry['_id']) + ","
    return res

@app.route('/deleterules')
def delrules():
    source = request.args.get('source')
    des = request.args.get('destination')
    protocol = request.args.get('protocol')
    rules.delete_many({"source": source, "destination": des, "protocol": protocol.lower()})
    return redirect('http://localhost/gui/index2.html')

@app.route("/testform")
def do_post_search():
    source = request.args.get('source')
    des = request.args.get('destination')
    protocol = request.args.get('protocol')
    rules.insert_one({"source": source, "destination": des, "protocol": protocol.lower()})
    return redirect('http://localhost/gui/index2.html')


app.run(debug=False, port=80, host='0.0.0.0')
