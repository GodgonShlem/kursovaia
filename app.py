from flask import Flask, render_template, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

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

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html', active_page='home')

@app.route('/lessons', methods=['GET','POST'])
def lessons():
    return render_template('lessons.html', active_page='lessons')

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

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)