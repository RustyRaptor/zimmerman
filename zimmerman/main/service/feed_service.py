import os
from glob import glob
from flask import url_for

from zimmerman.main import db
from zimmerman.main.model.main import (
    Post,
    Comment,
    Reply,
    PostLike,
    CommentLike,
    ReplyLike,
)
from zimmerman.main.service.like_service import check_like
from zimmerman.main.service.post_service import load_author

# Import Schema
from zimmerman.main.model.main import PostSchema, CommentSchema, ReplySchema

# Import upload path
from .upload_service import get_image


def uniq(a_list):
    encountered = set()
    result = []
    for elem in a_list:
        if elem not in encountered:
            result.append(elem)
        encountered.add(elem)
    return result


def get_comments(post_info, current_user_id):
    comments = []
    comment_schema = CommentSchema()
    # Get the first five comments
    for comment_id in sorted(post_info["comments"])[:5]:
        # Get the coment info
        comment = Comment.query.filter_by(id=comment_id).first()
        comment_info = comment_schema.dump(comment)

        comment_info["author"] = load_author(comment_info["creator_public_id"])

        # Check if the comment is liked
        user_likes = CommentLike.query.filter_by(on_comment=comment_id).order_by(
            CommentLike.liked_on.desc()
        )

        if check_like(user_likes, current_user_id):
            comment_info["liked"] = True
        else:
            comment_info["liked"] = False

        if comment_info['replies']:
            comment_info['initial_replies'] = get_replies(comment_info, current_user_id)

        comments.append(comment_info)

    return comments


def get_replies(comment_info, current_user_id):
    replies = []
    reply_schema = ReplySchema()

    # Get the latest 2 replies if they are existent
    for reply_id in sorted(comment_info["replies"])[:2]:
        reply = Reply.query.filter_by(id=reply_id).first()
        reply_info = reply_schema.dump(reply)

        reply_info["author"] = load_author(reply_info["creator_public_id"])

        # Check if the reply is liked
        user_likes = ReplyLike.query.filter_by(on_reply=reply_id).order_by(
            ReplyLike.liked_on.desc()
        )

        if check_like(user_likes, current_user_id):
            reply_info["liked"] = True
        else:
            reply_info["liked"] = False

        replies.append(reply_info)

    return replies


class Feed:
    def get_chronological():
        # Get Posts IDs by latest creation (chronological order)
        # Get Posts info
        posts = Post.query.with_entities(Post.id, Post.created).order_by(
            Post.created.desc()
        )
        # WIP
        print(posts)

    def get_activity():
        # Get Posts IDs by latest activity (latest comment on post)
        # Get Posts info
        posts = Post.query.with_entities(Post.id, Post.created).all()
        post_schema = PostSchema(many=True)
        post_info = post_schema.dump(posts)

        # Comments
        comments = Comment.query.all()
        comment_schema = CommentSchema(many=True)
        comment_info = comment_schema.dump(comments)

        # Get the activity based on the latest comments
        post_activity_from_comments = [
            {"id": c["post"], "created": c["created"]} for c in comment_info
        ]

        feed = uniq(
            x["id"]
            for x in sorted(
                post_activity_from_comments + post_info,
                key=lambda x: x["created"],
                reverse=True,
            )
        )

        response_object = {
            "success": True,
            "message": "Post IDs sent to client.",
            "post_ids": feed,
        }
        return response_object, 200

    def get_posts_info(id_array, current_user):
        # Get the data in the array of post IDs
        post_schema = PostSchema()
        posts = []

        if len(id_array) == 0 or id_array is None:
            response_object = {
                "success": True,
                "message": "There is nothing to send.",
                "posts": posts
            }
            return response_object, 200

        for post_id in id_array:
            # Get the post and schema
            post = Post.query.filter_by(id=post_id).first()
            # Dump the data and append it to the posts list
            post_info = post_schema.dump(post)

            # Add the author
            post_info["author"] = load_author(post_info["creator_public_id"])

            # Check if the current user has liked the post
            user_likes = PostLike.query.filter_by(on_post=post.id).order_by(
                PostLike.liked_on.desc()
            )

            if check_like(user_likes, current_user.id):
                post_info["liked"] = True
            else:
                post_info["liked"] = False

            # Check if it has an image
            if post_info["image_file"]:
                # Get the image_url
                post_info["image_url"] = get_image(
                    post_info["image_file"], "postimages"
                )

            # Get the latest 5 comments
            if post_info["comments"]:
                post_info["initial_comments"] = get_comments(post_info, current_user.id)

            posts.append(post_info)

        response_object = {
            "success": True,
            "message": "Post data successfully delivered.",
            "posts": posts,
        }
        return response_object, 200
