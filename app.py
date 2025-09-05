import random
import string
import time

from authlib.integrations.flask_oauth2 import current_token
from flask import Flask, g, request, jsonify
from flask_oidc import OpenIDConnect
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_scheduler import Scheduler

import models

app = Flask(__name__)
app.config['OIDC_RESOURCE_SERVER_ONLY'] = True
app.config['OIDC_CLIENT_SECRETS'] = 'client_secrets.json'
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
oidc = OpenIDConnect(app)
scheduler = Scheduler(app)
membership_tokens = {}


@scheduler.runner(interval=5)
def purge_expired_token():
    try:
        for k, v in membership_tokens.items():
            if v.is_expired():
                membership_tokens.pop(k)
    except Exception as e:
        app.logger.exception(e)


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
    membership_tokens[code] = models.MembershipToken(profile['name'], profile['email'], time.time() + 300)
    return jsonify({"code": code})

@app.route('/validate_code/<code>')
def validate_code(code):
    token = membership_tokens.get(code)
    if token and not token.is_expired():
        return jsonify({"name": token.name, "email": token.email, "valid": True})
    return jsonify({"error": "Invalid or expired token.", "valid": False}), 400

if __name__ == '__main__':
    app.run()
