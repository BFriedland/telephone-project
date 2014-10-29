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
import psycopg2


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY', 'sooperseekritvaluenooneshouldknow'
)

app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL', 'dbname=telephone_db user=store'
)


def connect_db():
    """Return a connection to the configured database"""
    if 'DATABASE' not in app.config:
        app.config['DATABASE'] = os.environ.get(
            'DATABASE_URL', 'dbname=telephone_db user=store')

    return psycopg2.connect(app.config['DATABASE'])


def init_db():
    """Initialize the database.
    WARNING: This will drop existsing tables"""
    with closing(connect_db()) as db:
        db.cursor().execute(game.DB_DROP_TABLES)
        db.commit()
        db.cursor().execute(game.PROMPT_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(game.IMAGE_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(game.GAME_TABLE_SCHEMA)
        db.commit()


def requires_username(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            fakenames = ['Homer', 'Marge', 'Bart', 'Lisa', 'Maggie', 'Krusty',
                         'Itchy', 'Scratchy', 'Dr. Hibbert', 'Nelson', 'Jimbo']
            session['username'] = random.sample(fakenames, 1)[0]

        return view(*args, **kwargs)
    return decorated


@requires_username
def store_drawing(drawing_data):
    print drawing_data
    print session['username']


@requires_username
def get_drawing(step_to_complete):
    pass


@requires_username
def get_first_prompt():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(game.connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(game.DB_GET_FIRST_PROMPT_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(game.DB_GET_FIRST_PROMPT_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        first_prompts = p1.intersection(p2)
        db.commit()
    return  first_prompts.pop()


@requires_username
def get_second_prompt():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(game.connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(game.DB_GET_SECOND_PROMPT_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(game.DB_GET_SECOND_PROMPT_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        second_prompts = p1.intersection(p2)
        db.commit()
    return  second_prompts.pop()

@requires_username
def get_first_image():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(game.connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(game.DB_GET_FIRST_IMAGE_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(game.DB_GET_FIRST_IMAGE_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        first_images = p1.intersection(p2)
        db.commit()
    return  first_images.pop()

@requires_username
def get_second_image():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(game.connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(game.DB_GET_SECOND_IMAGE_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(game.DB_GET_SECOND_IMAGE_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        second_images = p1.intersection(p2)
        db.commit()
    return  second_images.pop()

@requires_username
def create_game():
    # execute a DB_CREATE_GAME script, RETURNING id for the game
    with closing(connect_db()) as db:
        cur = db.cursor()
        cur.execute(game.DB_CREATE_GAME)
        game_id = cur.fetchone()[0]
        db.commit()
        return game_id


@requires_username
def store_data(game_column, tablename, data):
    ''' Accepts a PSQL content table name and data to store in that table,
    inserts the data, and conducts a join on the games table. '''
    if not data:
        raise ValueError('Prompt data not supplied to store_prompt')

    # If this is the first prompt in a series, create a new game
    # and store its id in the session cookie.
    if game_column == 'first_prompt_id':
        session['game_id'] = create_game()

    with closing(connect_db()) as db:
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


@requires_username
def store_first_prompt(prompt):
    if not prompt:
        raise ValueError('Prompt data not supplied to store_first_prompt')

    with closing(connect_db()) as db:
        cur = db.cursor()
        tablename = 'prompts'
        username = session['username']
        now = datetime.datetime.utcnow()
        cur.execute(game.DB_INSERT_CONTENT, [tablename, username, prompt, now])
        db.commit()


@requires_username
def get_games():
    """Return a list of dictionaries containing gameids for games that
    the current user has contributed to"""
    return [{'id': 1}, {'id': 2}]


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
                'prompt': get_first_prompt()}
    return json.dumps(response)


@app.route('/step_three', methods=['POST'])
@requires_username
def step_three():
    store_data('first_image_id', 'images', json.dumps(request.json))
    response = {'html': render_template('step_three.html'),
                'drawing': get_first_image()}
    return json.dumps(response)


@app.route('/step_four', methods=['POST'])
@requires_username
def step_four():
    store_data('second_prompt_id', 'prompts', request.form['prompt'])
    response = {'html': render_template('step_two.html'),
                'prompt': get_second_prompt()}
    return json.dumps(response)


@app.route('/step_five', methods=['POST'])
@requires_username
def step_five():
    store_data('second_image_id', 'images', json.dumps(request.json))
    response = {'html': render_template('step_three.html'),
                'drawing': get_second_image()}
    return json.dumps(response)


@app.route('/final', methods=['POST'])
@requires_username
def final_step():
    store_data('third_prompt_id', 'prompts', request.form['prompt'])
    return 'OK'


@app.route('/show_games')
@requires_username
def show_games():
    games = get_games()
    return render_template('show_games.html',
                           user=session['username'],
                           games=games)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username'].encode('utf-8')
        return redirect(url_for('home'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
