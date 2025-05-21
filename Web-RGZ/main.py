from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_babel import Babel, gettext as _, lazy_gettext as _l
from flask_wtf.file import FileAllowed
import os
import jwt
import datetime
import smtplib
import random
import string
import uuid
from functools import wraps
from itsdangerous import URLSafeTimedSerializer
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    file = FileField('Video File', validators=[
        DataRequired(),
        FileAllowed(['mp4'], 'Only MP4 videos are allowed!')
    ])

app = Flask(__name__)

app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['LANGUAGES'] = {
    'en': 'English',
    'ru': 'Русский'
}

babel = Babel(app)
app.config['SECRET_KEY'] = 'Ваш секретный ключ' // Укажите какой либо набор букв/цифр/спец символов
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'webm', 'ogg'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 10  # 1GB
app.config['MAIL_SERVER'] = 'Сервис' // Ваш сервис почты
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ВашаПочта@адрес' // Почтовый ящик
app.config['MAIL_PASSWORD'] = 'Пароль' // Пароль от вашей почты
app.config['MAIL_DEFAULT_SENDER'] = 'ВашаПочта@адрес' // Почтовый ящик
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'

db = SQLAlchemy(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    videos = db.relationship('Video', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

class VerificationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    filename = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='video', lazy=True)
    likes = db.relationship('Like', backref='video', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    
with app.app_context():
    db.create_all()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user or not current_user.verified:
                return redirect(url_for('login'))
        except:
            return redirect(url_for('login'))
        return f(current_user, *args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def generate_unique_filename(filename):
    """Генерирует уникальное имя файла для предотвращения коллизий"""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{ext}"

def send_verification_email(email, code):
    try:
        subject = "Ваш код подтверждения для Loomix"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Poppins', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    color: #6c5ce7;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .code-container {{
                    background-color: #f5f6fa;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .code {{
                    font-size: 28px;
                    letter-spacing: 5px;
                    color: #6c5ce7;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 14px;
                    color: #777;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #6c5ce7;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">Loomix</div>
                <h2>Подтверждение электронной почты</h2>
            </div>
            
            <p>Спасибо за регистрацию на Loomix! Для завершения регистрации, пожалуйста, используйте следующий код подтверждения:</p>
            
            <div class="code-container">
                <div class="code">{code}</div>
            </div>
            
            <p>Этот код действителен в течение 1 часа. Если вы не запрашивали этот код, пожалуйста, проигнорируйте это письмо.</p>
            
            <div class="footer">
                <p>С уважением,<br>Команда Loomix</p>
                <p>© {datetime.datetime.now().year} Loomix. Все права защищены.</p>
            </div>
        </body>
        </html>
        """

        text = f"""
        Подтверждение электронной почты для Loomix
        ========================================
        
        Ваш код подтверждения: {code}
        
        Введите этот код в приложении для завершения регистрации.
        Код действителен в течение 1 часа.
        
        Если вы не запрашивали этот код, пожалуйста, проигнорируйте это письмо.
        
        С уважением,
        Команда Loomix
        """
        
        message = f"""From: {app.config['MAIL_DEFAULT_SENDER']}
To: {email}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary"

--boundary
Content-Type: text/plain; charset=utf-8

{text}

--boundary
Content-Type: text/html; charset=utf-8

{html}

--boundary--
"""
        
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(app.config['MAIL_DEFAULT_SENDER'], email, message.encode('utf-8'))
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def get_locale():
    lang = request.args.get('lang')
    if lang in app.config['LANGUAGES']:
        return lang
    lang = session.get('lang')
    if lang in app.config['LANGUAGES']:
        return lang
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

babel.init_app(app, locale_selector=get_locale)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        videos = Video.query.join(User).filter(
            (Video.title.ilike(f'%{query}%')) | 
            (User.username.ilike(f'%{query}%'))
        ).all()
    else:
        videos = Video.query.all()
    return render_template('index.html', videos=videos)

@app.context_processor
def inject_locale():
    return dict(
        get_locale=get_locale,
        current_language=get_locale()
    )

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user_data = {
            'username': username,
            'email': email,
            'password': password
        }
        token = serializer.dumps(user_data)
        
        code = generate_verification_code()
        if not send_verification_email(email, code):
            flash('Failed to send verification email')
            return redirect(url_for('register'))
        
        new_code = VerificationCode(email=email, code=code)
        db.session.add(new_code)
        db.session.commit()
        
        return redirect(url_for('access_code', token=token))
    
    return render_template('register.html')

@app.route('/verify-email/<token>', methods=['GET', 'POST'])
def access_code(token):
    try:
        user_data = serializer.loads(token, max_age=3600)
    except:
        flash('Invalid or expired token')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        code = request.form['code']
        email = user_data['email']
        
        verification_code = VerificationCode.query.filter_by(email=email, code=code).first()
        if not verification_code:
            flash('Invalid verification code')
            return redirect(url_for('access_code', token=token))
        
        new_user = User(
            username=user_data['username'],
            email=email,
            password=user_data['password'],
            verified=True
        )
        db.session.add(new_user)
        db.session.delete(verification_code)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('access_code.html', email=user_data['email'], token=token)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            flash('Invalid credentials')
            return redirect(url_for('login'))
        
        if not user.verified:
            flash('Account not verified. Please check your email.')
            return redirect(url_for('login'))
        
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        
        response = redirect(url_for('index'))
        response.set_cookie('token', token)
        return response
    return render_template('login.html')

@app.route('/logout')
def logout():
    response = redirect(url_for('index'))
    response.set_cookie('token', '', expires=0)
    return response

@app.route('/upload', methods=['GET', 'POST'])
@token_required
def upload(current_user):
    form = UploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        title = form.title.data
        
        try:
            filename = generate_unique_filename(secure_filename(file.filename))
            upload_folder = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            if not os.path.exists(filepath):
                raise Exception("File was not saved correctly")
            if not filepath.lower().endswith('.mp4'):
                os.remove(filepath)
                flash('Only MP4 files are allowed', 'error')
                return render_template('upload.html', form=form)
            new_video = Video(
                title=title,
                filename=filename,
                user_id=current_user.id
            )
            db.session.add(new_video)
            db.session.commit()
            
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"Error during file upload: {e}")
            db.session.rollback()
            if 'filepath' in locals() and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting file: {e}")
            
            flash('Error uploading video. Please try again.', 'error')
    
    return render_template('upload.html', form=form)


@app.route('/video/<int:video_id>')
def video(video_id):
    video = Video.query.get_or_404(video_id)
    comments = Comment.query.filter_by(video_id=video_id).order_by(Comment.created_at.desc()).all()
    likes = Like.query.filter_by(video_id=video_id).count()
    return render_template('video.html', video=video, comments=comments, likes=likes)

@app.route('/comment/<int:video_id>', methods=['POST'])
@token_required
def comment(current_user, video_id):
    text = request.form['text']
    new_comment = Comment(text=text, user_id=current_user.id, video_id=video_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('video', video_id=video_id))

@app.route('/like/<int:video_id>', methods=['POST'])
@token_required
def like(current_user, video_id):
    existing_like = Like.query.filter_by(user_id=current_user.id, video_id=video_id).first()
    if existing_like:
        db.session.delete(existing_like)
    else:
        new_like = Like(user_id=current_user.id, video_id=video_id)
        db.session.add(new_like)
    db.session.commit()
    return redirect(url_for('video', video_id=video_id))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
