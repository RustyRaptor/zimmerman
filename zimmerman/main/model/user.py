from flask_login import UserMixin
from datetime import datetime

from .. import db, ma, bcrypt

# Alias common SQLAlchemy names
Column = db.Column
Model = db.Model

roles_users = db.Table('roles_users',
        Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(UserMixin, Model):
  """ User Model for storing user related details """

  # Basic details
  id = Column(db.Integer, primary_key=True)
  public_id = Column(db.String(15), unique=True)
  email = Column(db.String(255), unique=True, nullable=False)
  username = Column(db.String(20), unique=True)
  first_name = Column(db.String(50), nullable=True)
  last_name = Column(db.String(50), nullable=True)

  password_hash = Column(db.String(255))

  # Extra details
  bio = Column(db.Text, nullable=True)
  profile_picture = Column(db.String(35), nullable=True)

  # Post related
  posts = db.relationship('Posts', backref='user')

  post_likes = db.relationship('PostLike', backref='user')
  comment_likes = db.relationship('CommentLike', backref='user')
  reply_likes = db.relationship('ReplyLike', backref='user')

  # Status
  joined_date = Column(db.DateTime)
  roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('users'), lazy='dynamic')

  @property
  def password(self):
    raise AttributeError('Password: Write-Only field')

  @password.setter
  def password(self, password):
    self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
  
  def check_password(self, password):
    return bcrypt.check_password_hash(self.password_hash, password)

  def __repr__(self):
    return "<User '{}'>".format(self.username)

class Role(Model):
    """ Role Model for storing role related details """
    __tablename__ = "role"

    id = Column(db.Integer(), primary_key=True)
    name = Column(db.String(20), unique=True)
    description = Column(db.String(50))

    def __repr__(self):
        return '{} - {}'.format(self.name, self.id)

class Posts(Model):
    """ Post Model for storing post related details """
    
    # Basic details
    id = Column(db.Integer, primary_key=True)
    public_id = Column(db.String(15))
    owner_id = Column(db.Integer, db.ForeignKey('user.id'))
    creator_public_id = Column(db.String(15))

    # Post content and details
    content = Column(db.Text)
    image_file = Column(db.String(35), default=None, nullable=True)
    status = Column(db.String(10))

    created = Column(db.DateTime, default=datetime.utcnow)
    edited = Column(db.Boolean, default=False)

    likes = db.relationship('PostLike', backref='posts')
    comments = db.relationship('Comments', backref='posts')

    def __repr__(self):
      return "<Post '{}'>".format(self.id)

class Comments(Model):
    """ Comment Model for storing comment related details """

    # Basic details
    id = Column(db.Integer, primary_key=True)
    creator_public_id = Column(db.String(15))
    on_post = Column(db.Integer, db.ForeignKey('posts.id'))

    # Comment content and details
    content = Column(db.Text)
    created = Column(db.DateTime, default=datetime.utcnow)
    edited = Column(db.Boolean, default=False)

    likes = db.relationship('CommentLike', backref='comments')

    def __repr__(self):
      return "<Comment '{}'>".format(self.id)

class Reply(Model):
    """ Reply Model for storing reply related details """

    # Basic details
    id = Column(db.Integer, primary_key=True)
    creator_public_id = Column(db.String(15))
    on_comment = Column(db.Integer, db.ForeignKey('comments.id'))

    # Reply content and details
    content = Column(db.Text)
    created = Column(db.DateTime, default=datetime.utcnow)
    edited = Column(db.Boolean, default=False)

    likes = db.relationship('ReplyLike', backref='reply')

    def __repr__(self):
      return "<Reply '{}'>".format(self.id)

class PostLike(Model):
    """ PostLike Model for storing post like related details """

    # Details
    id = Column(db.Integer, primary_key=True)
    on_post = Column(db.Integer, db.ForeignKey('posts.id'))
    owner_id = Column(db.Integer, db.ForeignKey('user.id'))
    liked_on = Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
      return "<PostLike on Post '{}'>".format(self.on_post)

class CommentLike(Model):
    """ CommentLike Model for storing comment like related details """

    # Details
    id = Column(db.Integer, primary_key=True)
    on_comment = Column(db.Integer, db.ForeignKey('comments.id'))
    owner_id = Column(db.Integer, db.ForeignKey('user.id'))
    liked_on = Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
      return "<CommentLike on Comment '{}'>".format(self.on_comment)

class ReplyLike(Model):
    """ ReplyLike Model for storing reply like related details """

    # Details
    id = Column(db.Integer, primary_key=True)
    on_reply = Column(db.Integer, db.ForeignKey('reply.id'))
    owner_id = Column(db.Integer, db.ForeignKey('user.id'))
    liked_on = Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
      return "<ReplyLike on Reply '{}'>".format(self.on_comment)

# Model Schemas
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class PostSchema(ma.ModelSchema):
    class Meta:
        model = Posts

class CommentSchema(ma.ModelSchema):
    class Meta:
        model = Comments

class ReplySchema(ma.ModelSchema):
    class Meta:
        model = Reply

class PostLikeSchema(ma.ModelSchema):
    class Meta:
        model = PostLike