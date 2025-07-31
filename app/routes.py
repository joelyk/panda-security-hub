from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from app import db, socketio, login_manager
from app.models import User, Article, Comment, ChatMessage
from flask_socketio import emit
from datetime import datetime
import os
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

# Configuration de Flask-Mail
mail = Mail()

# Initialisation du compteur de visiteurs
visitor_count = 0

# Dossier pour stocker les images
UPLOAD_FOLDER = 'app/static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    global visitor_count
    visitor_count += 1
    articles = Article.query.order_by(Article.date_posted.desc()).all()
    messages = ChatMessage.query.order_by(ChatMessage.date_posted.asc()).all()
    return render_template('index.html', articles=articles, visitor_count=visitor_count, messages=messages)

@bp.route('/article/<int:article_id>', methods=['GET', 'POST'])
def article(article_id):
    article = Article.query.get_or_404(article_id)
    if request.method == 'POST' and current_user.is_authenticated:
        content = request.form['content']
        comment = Comment(content=content, user_id=current_user.id, article_id=article.id)
        db.session.add(comment)
        db.session.commit()
        flash('Commentaire ajouté ! ✅', 'success')
        return redirect(url_for('main.article', article_id=article.id))
    comments = Comment.query.filter_by(article_id=article.id).all()
    return render_template('article.html', article=article, comments=comments)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Connexion réussie ! ✅', 'success')
            return redirect(url_for('main.dashboard'))  # Redirige vers le dashboard
        flash('Email ou mot de passe incorrect. 🚫', 'danger')
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Cet email est déjà utilisé. Veuillez en choisir un autre. 🚫', 'danger')
            return redirect(url_for('main.register'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Compte créé ! Vous pouvez vous connecter. ✅', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté. 🚪', 'success')
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not (current_user.can_publish or current_user.is_admin):
        flash('Vous n\'êtes pas autorisé à publier des articles. 🚫', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        summary = request.form['summary']
        youtube_url = request.form['youtube_url'] if 'youtube_url' in request.form else None
        image_filename = 'placeholder.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_filename = filename
        article = Article(title=title, content=content, summary=summary, image=image_filename, youtube_url=youtube_url, user_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        flash('Article publié ! 📝', 'success')
        return redirect(url_for('main.dashboard'))
    articles = Article.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', articles=articles)

@bp.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à modifier cet article. 🚫', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        article.summary = request.form['summary']
        if 'youtube_url' in request.form:
            article.youtube_url = request.form['youtube_url']
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                article.image = filename
        db.session.commit()
        flash('Article modifié ! ✅', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_article.html', article=article)

@bp.route('/delete_article/<int:article_id>', methods=['POST'])
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à supprimer cet article. 🚫', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(article)
    db.session.commit()
    flash('Article supprimé ! 🗑️', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        flash('Accès réservé aux administrateurs. 🚫', 'danger')
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@bp.route('/toggle_publish/<int:user_id>', methods=['POST'])
@login_required
def toggle_publish(user_id):
    if not current_user.is_admin:
        flash('Accès réservé aux administrateurs. 🚫', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    user.can_publish = not user.can_publish
    db.session.commit()
    flash(f'Autorisation de publication {"activée" if user.can_publish else "désactivée"} pour {user.username}. ✅', 'success')
    return redirect(url_for('main.admin'))

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/services')
def services():
    return render_template('services.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        msg = Message('Nouveau message de contact', sender=email, recipients=['your-email@example.com'])
        msg.body = f"Nom: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)
        flash('Message envoyé ! Nous vous contacterons bientôt. 📧', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html')

@socketio.on('message')
def handle_message(data):
    if current_user.is_authenticated:
        message = ChatMessage(content=data['message'], user_id=current_user.id, date_posted=datetime.utcnow())
        db.session.add(message)
        db.session.commit()
        emit('message', {'username': current_user.username, 'message': data['message']}, broadcast=True)

@socketio.on('connect')
def handle_connect():
    global visitor_count
    emit('visitor_count', {'count': visitor_count}, broadcast=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))