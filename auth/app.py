#!/usr/bin/python

import sys, time, base64
from flask import Flask, jsonify, request
from flask_cors import cross_origin
app = Flask(__name__)


START = time.time()

def elapsed():
    running = time.time() - START
    minutes, seconds = divmod(running, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

def error_response(code, description):
    result = jsonify({"code": code, "description": description})
    result.headers["WWW-Authenticate"] = "Basic realm=Todo"
    result.status_code = 401
    return result

@app.route('/ambassador/auth', methods=['POST'])
def root():
    # We're gonna do basic authentication with a hardcoded password
    # here, but we can replace this with anything we might want.

    token = request.json.get("authorization", None)
    if not token:
        return error_response("unauthorized", "bad username or password")

    parts = token.split()
    if parts[0] == "Basic":
        user, password = base64.decodestring(parts[1]).split(":")
        if password == "todo":
            return ('', 200)
        else:
            return error_response("unauthorized", "bad username or password")
    else:
        return error_response("invalid_header", "unrecognized authentication mechanism")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
