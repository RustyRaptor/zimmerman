from flask import request
from flask_restplus import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..util.dto import PostDto
from ..service.post_service import get_post, create_new_post, delete_post, update_post
from ..service.user_service import load_user


api = PostDto.api
_post = PostDto.post

@api.route('/get/<string:post_public_id>')
class PostGet(Resource):
    
    @api.doc('Get a specific post.',
        responses = {
            200: 'Post info has successfully been sent.',
            404: 'Post not found!'
        }
    )
    @jwt_required
    def get(self, post_public_id):
        return get_post(post_public_id)

@api.route('/create')
class PostCreate(Resource):

    @api.expect(_post, validate=True)
    @api.doc('Create a new post.', 
      responses = {
            201: 'Post created',
            401: 'Something went wrong during the process'
      }
    )
    @jwt_required
    def post(self):
        """ Creates new post """
        data = request.get_json()
        current_user = load_user(get_jwt_identity())
        return create_new_post(data, current_user)
  
@api.route('/delete/<string:post_public_id>')
class PostDelete(Resource):

    @api.doc('Delete a post',
        responses = {
            200: 'Post has successfully been deleted',
            403: 'You do not have permission to delete the post',
            404: 'Post not found!'
        }
    )
    @jwt_required
    def delete(self, post_public_id):
        """ Deletes a post using its public id """
        current_user = load_user(get_jwt_identity())
        return delete_post(post_public_id, current_user)

@api.route('/update/<string:post_public_id>')
class PostUpdate(Resource):

    @api.expect(_post, validate=True)
    @api.doc('Update a post',
        responses = {
            200: 'Post has been updated',
            403: 'Post is locked or permission denied',
            404: 'Post not found!'
        }
    )
    @jwt_required
    def put(self, post_public_id):
        """ Updates a post using public id and new content """
        current_user = load_user(get_jwt_identity())
        data = request.get_json()
        return update_post(post_public_id, data, current_user)