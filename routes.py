from main import app
from flask import render_template, redirect, url_for, request, flash, session, jsonify
from modules import db, User, Tweet, Saved_itens, Notification, Follow
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename


@app.route('/')
def home():
    # if 'user_id' in session:
    #     return redirect(url_for('home'))
    return render_template("signin.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login realizado com sucesso!', 'success')
            users = User.query.limit(5).all()
            return render_template("home.html", users=users)
        else:
            flash('Email ou senha inválidos', 'error')
            return render_template("signin.html")
    return render_template("signin.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_birthday_str = request.form.get('user_birthday')

        try:
            user_birthday = datetime.strptime(user_birthday_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Data de nascimento inválida', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, user_birthday=user_birthday)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login.')
        return redirect(url_for('signin'))

    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.clear()
    return render_template('signin.html')

@app.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    tweets = Tweet.query.order_by(Tweet.created_at.desc()).all()
    return render_template('home.html', tweets=tweets)

@app.route('/post', methods=['POST'])
def post_tweet():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    content = request.form.get('content')
    if content:
        new_tweet = Tweet(content=content, user_id=session['user_id'])
        db.session.add(new_tweet)
        db.session.commit()
        flash('Tweet postado com sucesso!', 'success')
    
    return redirect(url_for('feed'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        results = Tweet.query.filter(Tweet.content.ilike(f'%{query}%')).all()
    return render_template('explore.html', results=results, query=query)

@app.route('/saved_items')
def saved_items():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    saved = Saved_itens.query.filter_by(user_id=session['user_id']).all()
    return render_template('saved_itens.html', saved_items=saved)

@app.route('/save_tweet/<int:tweet_id>')
def save_tweet(tweet_id):
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    existing = Saved_itens.query.filter_by(user_id=session['user_id'], tweet_id=tweet_id).first()
    if not existing:
        new_saved = Saved_itens(user_id=session['user_id'], tweet_id=tweet_id)
        db.session.add(new_saved)
        db.session.commit()
        flash('Tweet salvo com sucesso!', 'success')
    
    return redirect(request.referrer or url_for('home'))

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.id.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/follow/<int:user_id>')
def follow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    if session['user_id'] == user_id:
        flash('Você não pode seguir a si mesmo', 'error')
        return redirect(request.referrer or url_for('home'))
    
    existing = Follow.query.filter_by(follower_id=session['user_id'], followed_id=user_id).first()
    if not existing:
        new_follow = Follow(follower_id=session['user_id'], followed_id=user_id)
        db.session.add(new_follow)
        
        # Criar notificação
        user = User.query.get(session['user_id'])
        notification = Notification(
            user_id=user_id,
            message=f"{user.username} começou a te seguir"
        )
        db.session.add(notification)
        
        db.session.commit()
        flash('Usuário seguido com sucesso!', 'success')
    
    return redirect(request.referrer or url_for('home'))

@app.route('/profile/<username>')
@app.route('/profile')
def profile(username=None):
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    if not username:
        user = User.query.get(session['user_id'])
        return redirect(url_for('profile', username=user.username))
    
    user = User.query.filter_by(username=username).first_or_404()
    
    tweets = Tweet.query.filter_by(user_id=user.id).order_by(Tweet.created_at.desc()).all()
    followers_count = Follow.query.filter_by(followed_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()
    
    is_following = False
    if 'user_id' in session and user.id != session['user_id']:
        is_following = Follow.query.filter_by(
            follower_id=session['user_id'],
            followed_id=user.id
        ).first() is not None
    
    suggested_users = User.query.filter(
        User.id != session['user_id'],
        ~User.followers.any(Follow.follower_id == session['user_id'])
    ).limit(5).all()
    
    return render_template(
        'profile.html',
        user=user,
        tweets=tweets,
        tweets_count=len(tweets),
        followers_count=followers_count,
        following_count=following_count,
        is_following=is_following,
        suggested_users=suggested_users
    )

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    
    try:
        user.username = request.form.get('name', user.username)
        user.bio = request.form.get('bio', user.bio)
        # user.location = request.form.get('location', user.location)
        # user.website = request.form.get('website', user.website)
        
        if 'banner' in request.files:
            banner = request.files['banner']
            if banner.filename != '':
                filename = secure_filename(f"banner_{user.id}.jpg")
                banner.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.banner_picture = filename
        
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename != '':
                filename = secure_filename(f"avatar_{user.id}.jpg")
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_picture = filename
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/unfollow/<int:user_id>')
def unfollow(user_id):
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    follow = Follow.query.filter_by(
        follower_id=session['user_id'],
        followed_id=user_id
    ).first()
    
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash('Você deixou de seguir este usuário', 'success')
    
    return redirect(request.referrer or url_for('profile'))
