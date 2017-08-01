import json, urllib
from flask import request, jsonify, _app_ctx_stack
from functools import wraps
from jose import jwt

AUTH0_DOMAIN = "todo-rhs.auth0.com"
API_AUDIENCE = "todo"
ALGORITHMS = ["RS256"]

class AuthError(Exception):

    def __init__(self, response):
        self.response = response

# Format error response and append status code.
def handle_error(error, status_code):
    """Handles the errors
    """
    resp = jsonify(error)
    resp.status_code = status_code
    raise AuthError(resp)

def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    # This was the original code in auth0 example:
    #
    #     auth = request.headers.get("Authorization", None)
    #
    # The envoy extauth filter forwards headers as part of the POST
    # body, so we need to adjust it.
    auth = request.json.get("authorization", None)
    if not auth:
        return handle_error({"code": "authorization_header_missing",
                             "description":
                                 "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        return handle_error({"code": "invalid_header",
                             "description":
                                 "Authorization header must start with"
                                 "Bearer"}, 401)
    elif len(parts) == 1:
        return handle_error({"code": "invalid_header",
                             "description": "Token not found"}, 401)
    elif len(parts) > 2:
        return handle_error({"code": "invalid_header",
                             "description": "Authorization header must be"
                                            "Bearer token"}, 401)

    token = parts[1]
    return token

def requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    token_scopes = unverified_claims["scope"].split()
    for token_scope in token_scopes:
        if token_scope == required_scope:
            return True
    return False

jwks = None

def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()
            global jwks
            if jwks is None:
                jsonurl = urllib.urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
                jwks = json.loads(jsonurl.read())
            try:
                unverified_header = jwt.get_unverified_header(token)
            except jwt.JWTError:
                return handle_error({"code": "invalid_header",
                                     "description": "Invalid header. "
                                                    "Use an RS256 signed JWT Access Token"}, 401)
            if unverified_header["alg"] == "HS256":
                return handle_error({"code": "invalid_header",
                                     "description": "Invalid header. "
                                                    "Use an RS256 signed JWT Access Token"}, 401)
            rsa_key = {}
            for key in jwks["keys"]:
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
                        audience=API_AUDIENCE,
                        issuer="https://"+AUTH0_DOMAIN+"/"
                    )
                    print payload
                except jwt.ExpiredSignatureError:
                    return handle_error({"code": "token_expired",
                                         "description": "token is expired"}, 401)
                except jwt.JWTClaimsError:
                    return handle_error({"code": "invalid_claims",
                                         "description": "incorrect claims,"
                                                        " please check the audience and issuer"}, 401)
                except Exception:
                    return handle_error({"code": "invalid_header",
                                         "description": "Unable to parse authentication"
                                                        " token."}, 400)

                _app_ctx_stack.top.current_user = payload
                return f(*args, **kwargs)
            return handle_error({"code": "invalid_header",
                                 "description": "Unable to find appropriate key"}, 400)
        except AuthError, e:
            return e.response
    return decorated
