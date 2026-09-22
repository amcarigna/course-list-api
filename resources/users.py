import json
from flask import Blueprint, make_response
from flask_restful import Resource, Api, reqparse, fields, marshal_with, url_for
import models

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String
}

class UserList(Resource):
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', required=True, help='No username provided', location=['form', 'json'])
        self.reqparse.add_argument('email', required=True, help='No email provided', location=['form', 'json'])
        self.reqparse.add_argument('password', required=True, help='No password provided', location=['form', 'json'])
        self.reqparse.add_argument('verify_password', required=True, help='No password verification provided', location=['form', 'json'])
        super().__init__()
    
    
    @marshal_with(user_fields)
    def post(self):
        args = self.reqparse.parse_args()
        if args.get('password') == args.get('verify_password'):
            user = models.User.create_user(**args)
            return user, 201, {'Location': url_for('users.users')}
        return make_response(json.dumps({'error': "Passwords do not match."}), 400)


users_api = Blueprint('users', __name__)
api = Api(users_api)
api.add_resource(UserList, '/users', endpoint='users')

