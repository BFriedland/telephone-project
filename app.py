from __future__ import unicode_literals
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
import io
import json
import os
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY', 'sooperseekritvaluenooneshouldknow'
)


def requires_username(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return decorated


def store_drawing(drawing_data):
    filename = session['username'] + "_drawing"
    filename = "".join([c for c in filename if c.isalpha() or c.isdigit()
                        or c == '_']).strip()
    filename = filename + ".txt"
    with io.open(filename, 'wb') as tempfile:
        json.dump(drawing_data, tempfile)


def retrieve_drawing():
    filename = session['username'] + "_drawing"
    filename = "".join([c for c in filename if c.isalpha() or c.isdigit()
                        or c == '_']).strip()
    filename = filename + ".txt"

    try:
        with io.open(filename, 'r') as tempfile:
            drawing_data = json.load(tempfile)
    except(IOError):
        drawing_data = \
            json.dumps({"objects": [], "background": ""}).encode('utf-8')
            # This is a blank drawing

    return drawing_data


def get_prompt():
    return "A sample prompt is not very fun to draw."


def store_prompt():
    pass


@app.route('/')
def show_test_page():
    return render_template('test_page.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('show_test_page'))


@requires_username
@app.route('/new-drawing', methods=['POST'])
def receive_drawing():
    last_pic = retrieve_drawing()
    store_drawing(request.json)
    return last_pic


@app.route('/test')
def test():
    return render_template('base.html')


@app.route('/get-first-prompt')
def get_first_prompt():
    return get_prompt()


@app.route('/step_one')
def step_one():
    return render_template("step_one.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username'].encode('utf-8')
        return redirect(url_for('show_test_page'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
