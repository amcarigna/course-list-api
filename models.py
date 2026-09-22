import datetime as dt
from peewee import *
from argon2 import PasswordHasher
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
import config

HASHER = PasswordHasher()

class User(Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()
    
    class Meta:
        database = config.DATABASE
    
    
    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        email = email.lower()
        try:
            cls.select().where((cls.username**username) | (cls.email==email)).get()
        except cls.DoesNotExist:
            user = cls(username=username, email=email)
            user.password = User.set_password(password)
            user.save()
            return user
        else:
            raise Exception("User with that username or email already exists.")
    
    
    @staticmethod
    def verify_auth_token(token, max_age=3600):
        serializer = Serializer(config.SECRET_KEY)
        try:
            data = serializer.loads(token, max_age=max_age)
        except (SignatureExpired, BadSignature):
            return None
        user = User.get(User.id==data['id'])
        return user
    
    
    @staticmethod
    def set_password(password):
        return HASHER.hash(password)
    
    
    def verify_password(self, password):
        return HASHER.verify(self.password, password)
    
    
    def generate_auth_token(self):
        serializer = Serializer(config.SECRET_KEY)
        return serializer.dumps({'id': self.id})


class Course(Model):
    title = CharField()
    url = CharField(unique=True)
    created_at = DateTimeField(default=dt.datetime.now)
    
    class Meta:
        database = config.DATABASE


class Review(Model):
    course = ForeignKeyField(Course, related_name='review_set')
    rating = IntegerField()
    comment = TextField(default='')
    created_at = DateTimeField(default=dt.datetime.now)
    created_by = ForeignKeyField(User, related_name='review_set')
    
    class Meta:
        database = config.DATABASE


def initialize():
    config.DATABASE.connect()
    config.DATABASE.create_tables([User, Course, Review], safe=True)
    config.DATABASE.close()

