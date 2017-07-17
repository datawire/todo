#!/usr/bin/python

import sys, time
from flask import Flask, request
from flask_cors import cross_origin
from auth0 import requires_auth, requires_scope
app = Flask(__name__)


START = time.time()

def elapsed():
    running = time.time() - START
    minutes, seconds = divmod(running, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

@app.route('/ambassador/auth', methods=['POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@requires_auth
def root():
    return ('', 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
