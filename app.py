from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'QWERTYqwety123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///siteBases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UsersDB(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False) 
    status = db.Column(db.String(15), default='user', nullable=False) 
    password_hash = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.now)
    passed = db.relationship('UsersPassed', backref='username', lazy=True)

class Lessons(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    questions = db.relationship('Questions', backref='lesson', lazy=True)
    passed = db.relationship('UsersPassed', backref='lesson', lazy=True)

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answers = db.Column(db.Text, nullable=False)
    isCorrect = db.Column(db.Text, nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)

class UsersPassed(db.Model):
    __tablename__ = 'userspassed'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.ForeignKey('users.username'), nullable=False)
    is_passed = db.Column(db.String(300), default = False,nullable=False)
    lesson_id = db.Column(db.ForeignKey('lessons.id'), nullable=False)

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html', active_page='home')

@app.route('/lessons', methods=['GET','POST'])
def lessons():
    return render_template('lessons.html', active_page='lessons')

@app.route('/lessoncreate', methods=['GET','POST'])
def lessonsadmin():
    lessons = Lessons.query.all() 
    return render_template('lessoncreate.html', lessons=lessons, active_page='lessons')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create_lesson', methods=['GET', 'POST'])
def createlesson():
    if request.method == 'POST':
        try:
            lesson_title = request.form['lesson-title']
            lesson_text = request.form['lesson-text']
            lesson_questions = request.form.get('lesson-questions', '')
            answer_texts = request.form.getlist('answer-text')
            is_correct = request.form.getlist('is-correct')

            if not lesson_questions or not answer_texts or not is_correct:
                return jsonify({'response': False, 'message': 'Необходимо добавить вопрос и ответы'})
            
            images = request.files.getlist('lesson-images')
            image_paths = []
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            for i, image in enumerate(images):
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(UPLOAD_FOLDER, f"{i}_{filename}") 
                    image.save(image_path)
                    image_paths.append(image_path)
            
            for index, path in enumerate(image_paths):
                filename = os.path.basename(path) 
                lesson_text = lesson_text.replace(f"[img:{index + 1}]", f"<img src='/static/uploads/{filename}'>")

            new_lesson = Lessons(title=lesson_title, text=lesson_text)
            db.session.add(new_lesson)
            db.session.commit()
            answer_texts_json = json.dumps(answer_texts)
            is_correct_json = json.dumps(is_correct)
            new_question = Questions(question=lesson_questions, answers=answer_texts_json, isCorrect=is_correct_json, lesson_id=new_lesson.id)
            db.session.add(new_question)
            db.session.commit()
            return jsonify({'response': True})
        except Exception as err:
            db.session.rollback()
            return jsonify({'error': str(err)})

@app.route('/account', methods=['GET','POST'])
def account():
    return render_template('account.html', active_page='account')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        try:
            user_exist = db.session.query(UsersDB).filter_by(username=username).first()
            email_exist = db.session.query(UsersDB).filter_by(email=email).first()
            if user_exist:
                return jsonify({'error': 'Пользователь с таким именем уже существует'})
            elif email_exist:
                return jsonify({'error': 'Пользователь с такой почтой существует'})
            elif len(password)<8:
                return jsonify({'error': 'Пароль должен быть не меньше 8 символов'})
            elif password != password_confirm:
                return jsonify({'error': 'Пароли не совпадают'})
        except Exception as err:
            db.session.rollback()
            return jsonify({'error': 'При регистрации возникла ошибка: ' + str(err)})

        new_user = UsersDB(username=username, email=email, phone=phone, password_hash=generate_password_hash(password))
        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_session'] = username
            session['user_status'] = 'user'
            return jsonify({'response': True})
        except Exception as err:
            db.session.rollback()
            return jsonify({'error': 'При регистрации возникла ошибка: ' + str(err)})

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        email_in_db = db.session.query(UsersDB).filter_by(email=email).first()
        if email_in_db is not None and check_password_hash(email_in_db.password_hash, password):
            session['user_session'] = email_in_db.username
            session['user_status'] = email_in_db.status
            return jsonify({'response': True, 'message':'Вход успешен'})
        else:
            return jsonify({'response': False, 'message':'Неправильный логин или пароль'})
    else:
        return 'Ошибка'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('account'))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)