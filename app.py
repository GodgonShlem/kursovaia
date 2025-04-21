from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html', active_page='home')

@app.route('/lessons', methods=['GET','POST'])
def lessons():
    return render_template('lessons.html', active_page='lessons')

@app.route('/account', methods=['GET','POST'])
def account():
    return render_template('account.html', active_page='account')

if __name__ == "__main__":
    app.run(debug=True)