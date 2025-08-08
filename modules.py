from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # profile_picture = db.Column(db.String(200), default='default.jpg')
    user_birthday = db.Column(db.Date, nullable=False)
    bio = db.Column(db.String(280))

    # ... restante do código ...

    def __init__(self, username, email, password, user_birthday):
        self.username = username
        self.email = email
        self.password = password
        self.user_birthday = user_birthday

    def __repr__(self):
        return f'<User {self.username}>'
    
class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    content = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('tweets', lazy=True))

    def __init__(self, content, user_id):
        self.content = content
        self.user_id = user_id

    def __repr__(self):
        return f'<Tweet {self.id} by User {self.user_id}>'

class Saved_itens(db.Model):
    __tablename__ = 'saved_itens'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('saved_itens', lazy=True))
    tweet = db.relationship('Tweet', backref=db.backref('saved_itens', lazy=True))

    def __init__(self, user_id, tweet_id):
        self.user_id = user_id
        self.tweet_id = tweet_id

    def __repr__(self):
        return f'<Saved Item {self.id} by User {self.user_id} for Tweet {self.tweet_id}>'
    
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'

class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    follower = db.relationship('User', foreign_keys=[follower_id], backref=db.backref('following', lazy='dynamic'))
    followed = db.relationship('User', foreign_keys=[followed_id], backref=db.backref('followers', lazy='dynamic'))

    def __init__(self, follower_id, followed_id):
        self.follower_id = follower_id
        self.followed_id = followed_id

    def __repr__(self):
        return f'<Follow {self.id} from User {self.follower_id} to User {self.followed_id}>'
