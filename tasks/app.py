#!/usr/bin/python

import time
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo, ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://todo-db-0.todo-db,todo-db-1.todo-db,todo-db-2.todo-db:27017"
app.config["MONGO_DBNAME"] = "tasks"
mongo = PyMongo(app)

START = time.time()

def elapsed():
    running = time.time() - START
    minutes, seconds = divmod(running, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

@app.route('/', methods=["GET"])
def root():
    result = mongo.db.tasks.find(projection={"_id": False})
    time.sleep(0.5)
    return jsonify({"status": "ok",
                    "tasks": list(result)})

@app.route('/<tag>', methods=["POST"])
def add(tag):
    result = mongo.db.tasks.insert_one({"tag": tag, "task": request.json})
    return jsonify({"status": "ok", "id": str(result.inserted_id)})

@app.route('/<tag>', methods=["GET"])
def get(tag):
    result = list(mongo.db.tasks.find({"tag": tag}, projection={"_id": False}))
    if result:
        return jsonify(result[0])
    else:
        return ('Tag not found: %s\n' % tag, 404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
