from __future__ import unicode_literals
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
import json
import os
from functools import wraps
import random
import datetime
import game
from contextlib import closing


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY', 'sooperseekritvaluenooneshouldknow'
)

app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL', 'dbname=telephone_db user=store'
)


def requires_username(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            fakenames = ['Homer', 'Marge', 'Bart', 'Lisa', 'Maggie', 'Krusty',
                         'Itchy', 'Scratchy', 'Dr. Hibbert', 'Nelson', 'Jimbo']
            session['username'] = random.sample(fakenames, 1)[0]

        return view(*args, **kwargs)
    return decorated


def store_drawing(drawing_data):
    print drawing_data
    print session['username']


def get_drawing():
    return json.dumps({u'objects': [{u'opacity': 1, u'strokeMiterLimit': 10, u'height': 196, u'visible': True, u'stroke': u'rgb(0, 0, 0)', u'fill': None, u'angle': 0, u'flipX': False, u'flipY': False, u'top': 164.25, u'scaleX': 1, u'scaleY': 1, u'strokeLineJoin': u'round', u'width': 145, u'backgroundColor': u'', u'clipTo': None, u'type': u'path', u'strokeLineCap': u'round', u'strokeDashArray': None, u'strokeWidth': 30, u'originY': u'center', u'originX': u'center', u'path': [[u'M', 0, 0], [u'Q', 0, 0, 0.5, 0], [u'Q', 1, 0, 2.75, 0], [u'Q', 4.5, 0, 10.5, 0], [u'Q', 16.5, 0, 27.5, 0], [u'Q', 38.5, 0, 47.5, 0], [u'Q', 56.5, 0, 63.5, 0], [u'Q', 70.5, 0, 74, 0], [u'Q', 77.5, 0, 80, 0], [u'Q', 82.5, 0, 84.5, 1], [u'Q', 86.5, 2, 86.5, 24], [u'Q', 86.5, 46, 83, 74.5], [u'Q', 79.5, 103, 78, 113], [u'Q', 76.5, 123, 74, 131], [u'Q', 71.5, 139, 70.5, 146.5], [u'Q', 69.5, 154, 69.5, 155], [u'Q', 69.5, 156, 71, 153.5], [u'Q', 72.5, 151, 81.5, 141], [u'Q', 90.5, 131, 98, 124], [u'Q', 105.5, 117, 109.5, 114], [u'Q', 113.5, 111, 120.5, 106.5], [u'Q', 127.5, 102, 130, 105], [u'Q', 132.5, 108, 132.5, 127.5], [u'Q', 132.5, 147, 132.5, 157], [u'Q', 132.5, 167, 132, 174.5], [u'Q', 131.5, 182, 131, 187], [u'Q', 130.5, 192, 130.5, 194.5], [u'Q', 130.5, 197, 132.5, 196.5], [u'Q', 134.5, 196, 137, 194], [u'Q', 139.5, 192, 141.5, 189.5], [u'Q', 143.5, 187, 144.5, 185.5], [u'L', 145.5, 184]], u'shadow': None, u'pathOffset': {u'y': 0, u'x': 0}, u'left': 177.25}], u'background': u''}).encode('utf-8')


def get_prompt():
    return 'A sample prompt is not very fun to draw.'


def create_game():
    # execute a DB_CREATE_GAME script, RETURNING id for the game
    with closing(game.connect_db()) as db:
        cur = db.cursor()
        cur.execute(game.DB_CREATE_GAME)
        game_id = cur.fetchone()[0]
        db.commit()
        return game_id


def store_data(game_column, tablename, data):
    ''' Accepts a PSQL content table name and data to store in that table,
    inserts the data, and conducts a join on the games table. '''
    if not data:
        raise ValueError('Prompt data not supplied to store_prompt')

    # If this is the first prompt in a series, create a new game
    # and store its id in the session cookie.
    if game_column == 'first_prompt_id':
        session['game_id'] = create_game()

    with closing(game.connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        now = datetime.datetime.utcnow()
        if tablename == 'prompts':
            cur.execute(game.DB_INSERT_PROMPT,
                        [username, data, now])
        elif tablename == 'images':
            cur.execute(game.DB_INSERT_IMAGE,
                        [username, data, now])
        inserted_data_id = cur.fetchone()[0]

        # "Postgres made us do it." -- Jason
        execute_string = game.DB_UPDATE_GAMES % (game_column,
                                                 '%s', session['game_id'])
        cur.execute(execute_string,
                    [inserted_data_id])
        db.commit()


def store_first_prompt(prompt):
    if not prompt:
        raise ValueError('Prompt data not supplied to store_first_prompt')

    with closing(game.connect_db()) as db:
        cur = db.cursor()
        tablename = 'prompts'
        username = session['username']
        now = datetime.datetime.utcnow()
        cur.execute(game.DB_INSERT_CONTENT, [tablename, username, prompt, now])
        db.commit()


@app.route('/')
def home():
    return render_template('step_one.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/step_one')
def step_one():
    return render_template('step_one.html')


@app.route('/step_two', methods=['POST'])
@requires_username
def step_two():
    store_data('first_prompt_id', 'prompts', request.form['prompt'])
    response = {'html': render_template('step_two.html'),
                'prompt': get_prompt()}
    return json.dumps(response)


@app.route('/step_three', methods=['POST'])
@requires_username
def step_three():
    store_data('first_image_id', 'images', json.dumps(request.json))
    response = {'html': render_template('step_three.html'),
                'drawing': get_drawing()}
    return json.dumps(response)


@app.route('/step_four', methods=['POST'])
@requires_username
def step_four():
    store_data('second_prompt_id', 'prompts', request.form['prompt'])
    response = {'html': render_template('step_two.html'),
                'prompt': get_prompt()}
    return json.dumps(response)


@app.route('/step_five', methods=['POST'])
@requires_username
def step_five():
    store_data('second_image_id', 'images', json.dumps(request.json))
    response = {'html': render_template('step_three.html'),
                'drawing': get_drawing()}
    return json.dumps(response)


@app.route('/final', methods=['POST'])
@requires_username
def final_step():
    store_data('third_prompt_id', 'prompts', request.form['prompt'])
    return 'OK'


@app.route('/show_games')
@requires_username
def show_games():
    return render_template('show_games.html', user=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username'].encode('utf-8')
        return redirect(url_for('home'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
