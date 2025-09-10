import os
import random
import string
import traceback

import redis
from authlib.integrations.flask_oauth2 import current_token
from flask import Flask, g, request, jsonify
from flask_oidc import OpenIDConnect
from werkzeug.middleware.proxy_fix import ProxyFix

from models import MembershipToken

app = Flask(__name__)
app.config['OIDC_RESOURCE_SERVER_ONLY'] = True
app.config['OIDC_CLIENT_SECRETS'] = 'client_secrets.json'
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
oidc = OpenIDConnect(app)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', default='localhost'),
                           port=int(os.getenv('REDIS_PORT', default='6379')), db=0, decode_responses=True)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/me')
@oidc.accept_token(scopes=['openid', 'email', 'profile'])
def me():
    # https://github.com/fedora-infra/flask-oidc/issues/207
    auth = request.headers.get('Authorization')
    current_token["access_token"] = auth.split(None, 1)[1]
    profile = g._oidc_auth.userinfo(token=current_token)
    return jsonify(profile)


@app.route('/get_code')
@oidc.accept_token(scopes=['openid', 'email', 'profile'])
def get_code():
    auth = request.headers.get('Authorization')
    current_token["access_token"] = auth.split(None, 1)[1]
    profile = g._oidc_auth.userinfo(token=current_token)
    code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
    token = MembershipToken(name=profile['name'], email=profile['email'], username=profile['preferred_username'])
    redis_client.set(code, token.serialize(), ex=300)
    return jsonify({"code": code})


@app.route('/validate_code/<code>')
def validate_code(code):
    try:
        data = redis_client.get(code)
        token = MembershipToken.deserialize(data)
        if token:
            return jsonify({"token": dict(token), "valid": True})
        return jsonify({"error": "Invalid or expired token.", "valid": False}), 400
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Token deserialization error.", "valid": False}), 400


if __name__ == '__main__':
    app.run()
