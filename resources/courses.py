from flask import Blueprint, abort
from flask_restful import Resource, Api, reqparse, inputs, fields, marshal, marshal_with, url_for
import models
from auth import auth

course_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'reviews': fields.List(fields.String)
}


def add_reviews(course):
    course.reviews = [url_for('reviews.review', id=review.id) for review in course.review_set]
    return course


def course_or_404(course_id):
    try:
        course = models.Course.get(models.Course.id==course_id)
    except models.Course.DoesNotExist:
        abort(404, f"Course {course_id} does not exist.")
    else:
        return course


class CourseList(Resource):
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', required=True, help='No course title provided', location=['form', 'json'])
        self.reqparse.add_argument('url', required=True, help='No course url provided', location=['form', 'json'], type=inputs.url)
        super().__init__()
        

    def get(self):
        courses = [marshal(add_reviews(course), course_fields) for course in models.Course.select()]
        return {'courses': courses}
    
    
    @auth.login_required
    @marshal_with(course_fields)
    def post(self):
        args = self.reqparse.parse_args()
        course = models.Course.create(**args)
        return add_reviews(course), 201, {'Location': url_for('courses.course', id=course.id)}


class Course(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No course title provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required=True,
            help='No course URL provided',
            location=['form', 'json'],
            type=inputs.url
        )
        super().__init__()


    @marshal_with(course_fields)
    def get(self, id):
        return add_reviews(course_or_404(id))
    
    
    @auth.login_required
    @marshal_with(course_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Course.update(**args).where(models.Course.id==id)
        query.execute()
        return add_reviews(models.Course.get(models.Course.id==id)), 200, {'Location': url_for('courses.course', id=id)}
    
    
    @auth.login_required
    def delete(self, id):
        # i want to make sure there are no orphaned reviews, so delete the associated reviews too
        # delete the reviews first bc we have fk enforcement on i.e., there needs to be a parent. so delete the child first
        query = models.Review.delete().where(models.Review.course_id==id)
        query.execute()
        query = models.Course.delete().where(models.Course.id==id)
        query.execute()
        # the safer way to do this is with atomic(), look it up for details
        return '', 204, {'Location': url_for('courses.courses')}


courses_api = Blueprint('courses', __name__)
api = Api(courses_api)
api.add_resource(CourseList, '/courses', endpoint='courses')
api.add_resource(Course, '/courses/<int:id>', endpoint='course')

