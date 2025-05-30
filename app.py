from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
from werkzeug.utils import secure_filename
import uuid 
from functools import wraps  
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = 'QWERTYqwety123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///siteBases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    lessons = db.relationship('Lessons', backref='chapter', lazy=True) 

class UsersDB(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False) 
    status = db.Column(db.String(15), default='user', nullable=False) 
    password_hash = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.now)
    token = db.Column(db.String(100), unique=True, nullable=True) 
    passed = db.relationship('UsersPassed', backref='username', lazy=True)

class Lessons(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)
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

TOKEN_NAME = 'token'
COOKIE_DURATION = 30

def checkToken(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get(TOKEN_NAME)
        if token:
            user = UsersDB.query.filter_by(token=token).first()
            if user:
                session['user_session'] = user.username
                session['user_status'] = user.status
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    if 'user_session' not in session:
        token = request.cookies.get(TOKEN_NAME)
        if token:
            user = UsersDB.query.filter_by(token=token).first()
            if user:
                session['user_session'] = user.username
                session['user_status'] = user.status


@app.route('/', methods=['GET','POST'])
@checkToken
def index():
    return render_template('index.html', active_page='home')

@app.route('/lessons', methods=['GET','POST'])
@checkToken
def lessons():
    user_session = session.get('user_session')
    if user_session:
        chapters = Chapter.query.all()
        passed_lesson = UsersPassed.query.filter_by(user=session['user_session']).all()
        passed_lessons = set()
        for passed in passed_lesson:
            if passed.is_passed:
                passed_lessons.add(passed.lesson_id)
        its_next_lesson = set()
        if not passed_lessons and chapters:
            first_chapter = chapters[0]
            if first_chapter.lessons: 
                first_lesson = sorted(first_chapter.lessons, key=lambda x: x.id)[0] 
                its_next_lesson.add(first_lesson.id)
        else:
            for chapter in chapters:
                chapter_lessons = sorted([lesson for lesson in chapter.lessons if lesson.id not in passed_lessons], key=lambda x: x.id)
                if chapter_lessons:
                    its_next_lesson.add(chapter_lessons[0].id)
                    break 
        return render_template('lessons.html', active_page='lessons', chapters=chapters, passed_lessons=passed_lessons, its_next_lesson=its_next_lesson)
    else:
        return render_template('lessons.html', active_page='lessons')

@app.route('/lesson/<int:lesson_id>' , methods=['GET','POST'])
@checkToken
def lesson(lesson_id):
    current_lesson = Lessons.query.get_or_404(lesson_id) 
    if current_lesson:
        questions = Questions.query.filter_by(lesson_id=lesson_id).all()
        for question in questions:
            question.answer_load = json.loads(question.answers)
            question.isCorrect_load = json.loads(question.isCorrect)
        chapters = Chapter.query.all()
        passed_lesson = UsersPassed.query.filter_by(user=session['user_session']).all()
        passed_lessons = set()
        for passed in passed_lesson:
            if passed.is_passed:
                passed_lessons.add(passed.lesson_id)

        its_next_lesson = set() 
        if not passed_lessons and chapters:
            first_chapter = chapters[0]
            if first_chapter.lessons:
                first_lesson = sorted(first_chapter.lessons, key=lambda x: x.id)[0]
                its_next_lesson.add(first_lesson.id)
        else:
            for chapter in chapters:
                chapter_lessons = sorted([lesson for lesson in chapter.lessons if lesson.id not in passed_lessons], key=lambda x: x.id)
                if chapter_lessons:
                    its_next_lesson.add(chapter_lessons[0].id)
                    break
        if lesson_id in its_next_lesson or lesson_id in passed_lessons:
            next_lesson_id = None 
            for chapter in chapters:
                chapter_lessons = sorted(chapter.lessons, key=lambda lesson: lesson.id)
                for i, lesson in enumerate(chapter_lessons):
                    if lesson.id == lesson_id:
                        if i + 1 < len(chapter_lessons):
                            next_lesson_id = chapter_lessons[i + 1].id
                        break
                if next_lesson_id:
                    break
            return render_template('lesson.html', lesson=current_lesson, questions=questions, active_page='lessons', next_lesson=next_lesson_id)
        else:
            return redirect(url_for('lessons'))
    else:
        return redirect(url_for('lessons'))

@app.route('/lessoncreate', methods=['GET','POST'])
@checkToken
def lessonsadmin():
    chapters = Chapter.query.all()  
    lessons = Lessons.query.all() 
    return render_template('lessoncreate.html', lessons=lessons, chapters=chapters, active_page='lessons')

@app.route('/get_admin', methods=['GET','POST'])
@checkToken
def getadmin():
    if session['user_session']:
        user = UsersDB.query.filter_by(username=session['user_session']).first()
        user.status = 'admin'
        db.session.commit()
        session['user_status'] = 'admin'
        return redirect(url_for('account'))
    else: 
        return render_template('index.html', active_page='home')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create_lesson', methods=['GET', 'POST'])
@checkToken
def createlesson():
    if request.method == 'POST':
        try:
            lesson_title = request.form['lesson-title']
            lesson_text = request.form['lesson-text']
            chapter_id = request.form.get('chapter-select', type=int) 
            
            images = request.files.getlist('lesson-images')
            image_paths = []
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            total = len(images)
            for i, image in enumerate(images):
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(UPLOAD_FOLDER, f"{i}_{filename}") 
                    image.save(image_path)
                    image_paths.append(image_path)
            
            total = len(images)
            for index, path in enumerate(image_paths):
                filename = os.path.basename(path) 
                lesson_text = lesson_text.replace(f"[img:{total}]", f"<img src='/static/uploads/{filename}'>")
                total-=1

            new_lesson = Lessons(title=lesson_title, text=lesson_text, chapter_id=chapter_id) 
            db.session.add(new_lesson)
            db.session.commit()
            
            question_count = int(request.form['question-count'])
            for i in range(question_count):
                lesson_questions = request.form.get(f'lesson-question[{i}]')
                answer_texts = request.form.getlist(f'answer-text[{i}]')
                is_correct = request.form.getlist(f'is-correct[{i}]')

                if not lesson_questions or not answer_texts or not is_correct:
                    return jsonify({'response': False, 'message': 'Необходимо добавить вопрос и ответы'})
                
                answer_texts_json = json.dumps(answer_texts)
                is_correct_json = json.dumps(is_correct)
                new_question = Questions(question=lesson_questions, answers=answer_texts_json, isCorrect=is_correct_json, lesson_id=new_lesson.id)
                db.session.add(new_question)

            db.session.commit()
            return jsonify({'response': True})
        except Exception as err:
            db.session.rollback()
            return jsonify({'response': False, 'message': str(err)})

@app.route('/delete_lesson/<int:lesson_id>', methods=['DELETE'])
@checkToken
def deletelesson(lesson_id):
    lesson = Lessons.query.get(lesson_id)
    if lesson:
        Questions.query.filter_by(lesson_id=lesson_id).delete()
        UsersPassed.query.filter_by(lesson_id=lesson_id).delete()
        db.session.delete(lesson)
        db.session.commit()
        return ''
    else:
        return 'Урок не найден'

@app.route('/lessonedit/<int:lesson_id>', methods=['GET','POST'])
@checkToken
def lessonedit(lesson_id):
    lesson = Lessons.query.get_or_404(lesson_id) 
    lessons = Lessons.query.all()
    chapters = Chapter.query.all()
    questions = Questions.query.filter_by(lesson_id=lesson_id).all()
    for question in questions:
        question.answer_load = json.loads(question.answers)
        question.isCorrect_load = json.loads(question.isCorrect)
    return render_template('lessonedit.html', active_page='lessons', lesson=lesson, questions=questions, lessons=lessons, chapters=chapters)

@app.route('/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@checkToken
def editlesson(lesson_id):
    if request.method == 'POST':
        try:
            lesson = Lessons.query.get(lesson_id)
            if not lesson:
                return jsonify({'error': 'Урок не найден.'})

            chapter_id = request.form.get('chapter-select', type=int)
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
            lesson_text = request.form['lesson-text']
            total = len(images)
            for index, path in enumerate(image_paths):
                filename = os.path.basename(path) 
                lesson_text = lesson_text.replace(f"[img:{total}]", f"<img src='/static/uploads/{filename}'>")
                total-=1

            lesson.title = request.form['lesson-title']
            lesson.text = lesson_text
            lesson.chapter_id = chapter_id
            db.session.commit()

            question_count = int(request.form['question-count'])
            old_questions = Questions.query.filter_by(lesson_id=lesson_id).all()
            for q in old_questions:
                db.session.delete(q)
            db.session.commit()
            for i in range(question_count):
                lesson_questions = request.form.get(f'lesson-question[{i}]')
                answer_texts = request.form.getlist(f'answer-text[{i}]')
                is_correct = request.form.getlist(f'is-correct[{i}]')

                if not lesson_questions or not answer_texts or not is_correct:
                    return jsonify({'response': False, 'message': 'Необходимо добавить вопрос и ответы'})
                
                answer_texts_json = json.dumps(answer_texts)
                is_correct_json = json.dumps(is_correct)
                new_question = Questions(question=lesson_questions, answers=answer_texts_json, isCorrect=is_correct_json, lesson_id=lesson_id)
                db.session.add(new_question)
            db.session.commit()
            return jsonify({'response': True})

        except Exception as err:
            db.session.rollback()
            return jsonify({'response': False, 'message': str(err)})

@app.route('/account', methods=['GET','POST'])
@checkToken
def account():
    if 'user_session' not in session:
        return render_template('account.html', active_page='account')
    user = UsersDB.query.filter_by(username=session['user_session']).first()
    lessons_count = db.session.query(func.count(Lessons.id.distinct())).scalar()
    passed_lessons_count = db.session.query(func.count(UsersPassed.lesson_id.distinct())).filter(UsersPassed.user == session['user_session']).scalar()
    return render_template('account.html', active_page='account', user=user, lessons_count=lessons_count, passed_lessons_count=passed_lessons_count)

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

            response = jsonify({'response': True, 'message':'Вход успешен'})
            token = str(uuid.uuid4())
            email_in_db.token = token
            db.session.commit()
            expires = datetime.now() + timedelta(days=COOKIE_DURATION)
            response.set_cookie(TOKEN_NAME, token, expires=expires, httponly=True, samesite='Lax') 
            return response
        else:
            return jsonify({'response': False, 'message':'Неправильный логин или пароль'})
    else:
        return 'Ошибка'

@app.route('/test_verify/<int:lesson_id>', methods=['GET', 'POST'])
@checkToken
def testverify(lesson_id):
    if request.method == 'POST':
        questions = Questions.query.filter_by(lesson_id=lesson_id).all()
        results = []
        all_correct = True
        for question in questions:
            user_answers = request.form.getlist(f'test-checkbox-{question.id}')
            correct_answers = json.loads(question.isCorrect)

            is_correct = sorted(user_answers) == sorted(correct_answers)
            results.append({'question_id': question.id,'is_correct': is_correct})
            if not is_correct:
                all_correct = False

        if all_correct:
            try:
                alreadyPassed = UsersPassed.query.filter_by(user=session['user_session'], lesson_id=lesson_id, is_passed=True).first()
                if alreadyPassed:
                    return jsonify({'response': True, 'message': 'Всё верно (урок уже был пройден)','results': results})
                passed = UsersPassed(user=session['user_session'], lesson_id=lesson_id, is_passed=True)
                db.session.add(passed)
                db.session.commit()
                return jsonify({'response': True, 'message': 'Всё верно, тест засчитан','results': results})
            except Exception as err:
                db.session.rollback()
                return jsonify({'error': str(err)})
        else:
            return jsonify({'response': False, 'message': 'Есть ошибки','results': results}) 

@app.route('/logout')
@checkToken
def logout():
    username = session.get('user_session')
    if username:
        user = UsersDB.query.filter_by(username=username).first()
        if user and user.token:
            user.token = None 
            db.session.commit()

    session.clear()
    response = redirect(url_for('account'))
    response.delete_cookie(TOKEN_NAME) 
    return response

@app.route('/create_chapter', methods=['POST'])
@checkToken
def create_chapter():
    if request.method == 'POST':
        chapter_title = request.form.get('chapter-title')
        if not chapter_title:
            return jsonify({'response': False, 'message': 'Название главы не может быть пустым'})
        new_chapter = Chapter(title=chapter_title)
        db.session.add(new_chapter)
        db.session.commit()
        return jsonify({'response': True, 'message': 'Глава успешно создана'})

@app.route('/delete_chapter/<int:chapter_id>', methods=['DELETE'])
@checkToken
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter:
        for lesson in chapter.lessons:
            Questions.query.filter_by(lesson_id=lesson.id).delete()
            UsersPassed.query.filter_by(lesson_id=lesson.id).delete()
        Lessons.query.filter_by(chapter_id=chapter_id).delete()
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'response': True, 'message': 'Глава удалена'})
    else:
        return jsonify({'response': False, 'message': 'Глава не найдена'})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)