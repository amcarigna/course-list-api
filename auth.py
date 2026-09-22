from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
import models

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Token')
auth = MultiAuth(token_auth, basic_auth)


@basic_auth.verify_password
def verify_password(email_or_username, password):
    try:
        user = models.User.get((models.User.email == email_or_username) | (models.User.username == email_or_username))
    except models.User.DoesNotExist:
        return False
    
    if user.verify_password(password):
        g.user = user
        return True
    else:
        return False


@token_auth.verify_token
def verify_token(token):
    user = models.User.verify_auth_token(token)
    if user is not None:
        g.user = user
        return True
    return False

