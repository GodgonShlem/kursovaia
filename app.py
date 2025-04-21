from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/lessons', methods=['GET','POST'])
def lessons():
    return render_template('lessons.html')

@app.route('/account', methods=['GET','POST'])
def account():
    return render_template('account.html')

if __name__ == "__main__":
    app.run(debug=True)