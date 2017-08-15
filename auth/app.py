#!/usr/bin/python

import base64, json, os, sys, time, urllib, urlparse
from flask import Flask, g, jsonify, redirect, request
from jose import jwt
app = Flask(__name__)

class APIError(Exception):

    status_code = 400

    def __init__(self, code, description, status_code=None, payload=None):
        Exception.__init__(self)
        self.code = code
        self.description = description
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = dict(self.payload or ())
        result['code'] = self.code
        result['description'] = self.description
        return result

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

START = time.time()

def elapsed():
    running = time.time() - START
    minutes, seconds = divmod(running, 60)
    hours, minutes = divmod(minutes, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_API_AUDIENCE = os.environ["AUTH0_API_AUDIENCE"]

API_PROTO = os.environ["API_PROTO"]

ALGORITHMS = ["RS256"]

JWKS = None

@app.before_first_request
def jwks():
    global JWKS
    jsonurl = urllib.urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    JWKS = json.loads(jsonurl.read())

def get_authority():
    return request.json[":authority"]

def auth_url(url, scopes="email name profile"):
    params = {
        "audience": AUTH0_API_AUDIENCE,
        "scope": scopes,
        "response_type": "id_token token",
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": "%s://%s%s" % (API_PROTO, get_authority(), "/callback"),
        "nonce": "YOUR_CRYPTOGRAPHIC_NONCE",
        "state": "%s://%s%s" % (API_PROTO, get_authority(), url)
    }
    return "https://" + AUTH0_DOMAIN + "/authorize?" + urllib.urlencode(params)

def get_tokens():
    result = []

    # We first check for a bearer token in the authorization header,
    # and then if we don't find something we like there, we look in
    # the "access_token" cookie.
    auth_header = request.json.get("authorization", None)
    if auth_header:
        parts = auth_header.split()
        if len(parts) != 2:
            raise APIError("invalid_header", "no token found", 401)
        result.append((parts[0].lower(), parts[1]))

    # XXX: this cookie extraction should be replaced with standard
    # flask cookie API once we get the new ambassador plugin
    cookie = request.json.get("cookie", None)
    if cookie:
        params = urlparse.parse_qs(cookie)
        for k in list(params.keys()):
            params[k.strip()] = params[k]
        result.append(("bearer", params.get("access_token", [None])[0]))

    return result

def is_valid_bearer(token):
    if not token: return False

    print "URL:", request.url_root, request.headers.get("Host", None), request.json

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError, e:
        raise APIError("invalid_header", "Invalid header: %s" % e, 401)
    if unverified_header["alg"] == "HS256":
        raise APIError("invalid_header", "Invalid header. Use an RS256 signed JWT Access Token", 401)
    rsa_key = {}
    for key in JWKS["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_API_AUDIENCE,
                issuer="https://"+AUTH0_DOMAIN+"/")
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.JWTClaimsError, e:
            raise APIError("invalid_claims", "incorrect claims, please check the audience and issuer: %s" % e, 401)
        except Exception, e:
            raise APIError("invalid_header", "Unable to parse authentication token: %s" % e, 400)

# XXX: this is convenience for demo purposes and something a bit
#      smarter might make sense for dev/debug access, but definitely
#      change this if you want to use this code for a real application
def is_valid_basic(token):
    user, password = base64.decodestring(token).split(":")
    return password == "todo"

VALIDATORS = {
    "basic": is_valid_basic,
    "bearer": is_valid_bearer
}

def is_valid(type, token):
    return VALIDATORS[type](token)

AUTH_WHITELIST = ("/callback", "/health")
APP_WHITELIST = () # empty for now, but add any public paths here
WHITELIST = set(AUTH_WHITELIST + APP_WHITELIST)

@app.route('/ambassador/auth', methods=['POST'])
def root():
    url = request.json[":path"]
    path, query = urllib.splitquery(url)

    if path in WHITELIST:
        return ('', 200)

    for type, token in get_tokens():
        if is_valid(type, token):
            return ('', 200)

    return redirect(auth_url(url), code=302)

@app.route('/health')
def health():
    return ("OK", 200)

@app.route('/callback', methods=["GET", "POST"])
def callback():
    if "hash" in request.form:
        params = urlparse.parse_qs(request.form["hash"])
        access_token = params["access_token"][0]
        id_token = params["id_token"][0]
        expires_in = params["expires_in"][0]
        state = params["state"][0]
        response = redirect(state, code=302)
        response.set_cookie("access_token", access_token, secure=False, httponly=True)
        return response
    else:
        return (TRAMPOLINE, 200)

TRAMPOLINE = """<html>
<head>
  <title>Authentication</title>
</head>
<body onload="go()">
<script type="text/javascript">
function msg(text) {
    document.body.innerHTML = document.body.innerHTML + text + "<br>";
}

function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}

function go() {
    hash = window.location.hash.slice(1)
    post(window.location.href.split('#')[0], {hash: hash});
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
