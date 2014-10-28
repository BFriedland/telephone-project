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
            print 'Adding username'
            fakenames = ["Homer", "Marge", "Bart", "Lisa", "Maggie", "Krusty",
                         "Itchy", "Scratchy", "Dr. Hibbert", "Nelson", "Jimbo"]
            session['username'] = random.sample(fakenames, 1)[0]

        return view(*args, **kwargs)
    return decorated


def store_drawing(drawing_data):
    print drawing_data
    print session['username']


def retrieve_drawing():
    return json.dumps({"objects": [], "background": ""}).encode('utf-8')


def get_prompt():
    return "A sample prompt is not very fun to draw."


def create_game():
    # execute a DB_CREATE_GAME script, RETURNING id for the game
    with closing(game.connect_db()) as db:
        cur = db.cursor()
        cur.execute(game.DB_CREATE_GAME)
        game_id = cur.fetchone()[0]
        cur.commit()
        return game_id


def store_data(game_column, tablename, data):
    ''' Accepts a PSQL content table name and data to store in that table,
    inserts the data, and conducts a join on the games table. '''
    if not prompt:
        raise ValueError("Prompt data not supplied to store_prompt")

    # If this is the first prompt in a series, create a new game
    # and store its id in the session cookie.
    if game_column == "first_prompt_id":
        session['game_id'] = create_game()

    with closing(game.connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        now = datetime.datetime.utcnow()
        cur.execute(game.DB_INSERT_CONTENT, [tablename, username, data, now])
        inserted_data_id = cur.fetchone()[0]
        cur.commit()
        cur.execute(game.DB_UPDATE_GAMES,
                    [game_column, inserted_data_id, session['game_id']])
        cur.commit()


def store_first_prompt(prompt):
    if not prompt:
        raise ValueError("Prompt data not supplied to store_first_prompt")

    with closing(game.connect_db()) as db:
        con = get_database_connection()
        cur = con.cursor()
        tablename = 'prompts'
        username = session['username']
        now = datetime.datetime.utcnow()
        cur.execute(game.DB_INSERT_CONTENT, [tablename, username, prompt, now])
        cur.commit()


@app.route('/')
def home():
    return render_template('step_one.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/new-drawing', methods=['POST'])
@requires_username
def receive_drawing():
    store_drawing(request.json)
    return "OK"


@app.route('/new-prompt', methods=['POST'])
@requires_username
def receive_prompt():
    store_prompt(request.form['prompt'])
    return "OK"


@app.route('/step_one')
def step_one():
    return render_template("step_one.html")


@app.route('/step_two')
def step_two():
    prompt = get_prompt()
    return render_template("step_two.html", prompt=prompt)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username'].encode('utf-8')
        return redirect(url_for('home'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
