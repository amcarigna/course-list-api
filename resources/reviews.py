import json
from flask import Blueprint, abort, g, make_response
from flask_restful import Resource, Api, reqparse, inputs, fields, marshal, marshal_with, url_for
from peewee import IntegrityError
import models
from auth import auth

review_fields = {
    'id': fields.Integer,
    'for_course': fields.String,
    'rating': fields.Integer,
    'comment': fields.String(default=''),
    'created_at': fields.DateTime
}


def review_or_404(review_id):
    try:
        review = models.Review.get(models.Review.id==review_id)
    except models.Review.DoesNotExist:
        abort(404)
    else:
        return review
    

def add_course(review):
    review.for_course = url_for('courses.course', id=review.course.id)
    return review


class ReviewList(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('course', required=True, help='No course provided', location=['form', 'json'], type=inputs.positive)
        self.reqparse.add_argument('rating', required=True, help='No rating provided', location=['form', 'json'], type=inputs.int_range(1,5))
        self.reqparse.add_argument('comment', required=False, nullable=True, location=['form', 'json'], default='')
        super().__init__()


    def get(self):
        reviews = [marshal(add_course(review), review_fields) for review in models.Review.select()]
        return {'reviews': reviews}


    @auth.login_required
    @marshal_with(review_fields)
    def post(self):
        args = self.reqparse.parse_args()
        try:
            review = models.Review.create(created_by=g.user, **args)
        # bc im using fk enforcement at the db, it'll refuse to make a review for a non existent course (and throw an integrityerror). in that case, abort.
        except IntegrityError:
            abort(400, 'error: no course with that id.')
        else:
            return add_course(review), 201, {'Location': url_for('reviews.review', id=review.id)}


class Review(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'course',
            type=inputs.positive,
            required=True,
            help='No course provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'rating',
            type=inputs.int_range(1, 5),
            required=True,
            help='No rating provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'comment',
            required=False,
            nullable=True,
            location=['form', 'json'],
            default=''
        )
        super().__init__()


    @marshal_with(review_fields)
    def get(self, id):
        return add_course(review_or_404(id))
    
    
    @auth.login_required
    @marshal_with(review_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            review = models.Review.select().where(models.Review.created_by==g.user, models.Review.id==id).get()
        except models.Review.DoesNotExist:
            return make_response(json.dumps({'error': "That review doesn't exist or isn't accessible."}), 403)
        query = review.update(**args)
        query.execute()
        review = add_course(review)
        return review, 200, {'Location': url_for('reviews.review', id=id)}
    
    
    @auth.login_required
    def delete(self, id):
        try:
            review = models.Review.select().where(models.Review.created_by==g.user, models.Review.id==id).get()
        except models.Review.DoesNotExist:
            return make_response(json.dumps({'error': "That review doesn't exist or isn't accessible."}), 403)
        query = review.delete()
        query.execute()
        return '', 204, {'Location': url_for('reviews.reviews')}


reviews_api = Blueprint('reviews', __name__)
api = Api(reviews_api)
api.add_resource(ReviewList, '/reviews', endpoint='reviews')
api.add_resource(Review, '/reviews/<int:id>', endpoint='review')

