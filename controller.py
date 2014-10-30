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
import model
from contextlib import closing
import psycopg2


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY', 'sooperseekritvaluenooneshouldknow'
)

app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL', 'dbname=telephone_db user=store'
)

sorry_image = '{"objects": [{"opacity": 1, "strokeMiterLimit": 10, "height": 0, "visible": true, "stroke": "rgb(0, 0, 128)", "fill": null, "angle": 0, "flipX": false, "flipY": false, "top": 93, "scaleX": 1, "scaleY": 1, "strokeLineJoin": "round", "width": 1, "backgroundColor": "", "clipTo": null, "type": "path", "strokeLineCap": "round", "strokeDashArray": null, "strokeWidth": 30, "originY": "center", "originX": "center", "path": [["M", 0, 0], ["Q", 0, 0, 0.5, 0], ["L", 1, 0]], "shadow": null, "pathOffset": {"y": 0, "x": 0}, "left": 103.5}, {"opacity": 1, "strokeMiterLimit": 10, "height": 0, "visible": true, "stroke": "rgb(0, 0, 128)", "fill": null, "angle": 0, "flipX": false, "flipY": false, "top": 94, "scaleX": 1, "scaleY": 1, "strokeLineJoin": "round", "width": 1, "backgroundColor": "", "clipTo": null, "type": "path", "strokeLineCap": "round", "strokeDashArray": null, "strokeWidth": 30, "originY": "center", "originX": "center", "path": [["M", 0, 0], ["Q", 0, 0, 0.5, 0], ["L", 1, 0]], "shadow": null, "pathOffset": {"y": 0, "x": 0}, "left": 212.5}, {"opacity": 1, "strokeMiterLimit": 10, "height": 77, "visible": true, "stroke": "rgb(255, 0, 0)", "fill": null, "angle": 0, "flipX": false, "flipY": false, "top": 218.5, "scaleX": 1, "scaleY": 1, "strokeLineJoin": "round", "width": 181, "backgroundColor": "", "clipTo": null, "type": "path", "strokeLineCap": "round", "strokeDashArray": null, "strokeWidth": 12, "originY": "center", "originX": "center", "path": [["M", 0, 54], ["Q", 0, 54, 0.5, 54], ["Q", 1, 54, 0.75, 53.5], ["Q", 0.5, 53, 1, 51.5], ["Q", 1.5, 50, 3.5, 48.5], ["Q", 5.5, 47, 7.5, 44.5], ["Q", 9.5, 42, 11.5, 40.5], ["Q", 13.5, 39, 15.5, 37], ["Q", 17.5, 35, 20, 33], ["Q", 22.5, 31, 25, 29.5], ["Q", 27.5, 28, 30, 27], ["Q", 32.5, 26, 34.5, 25], ["Q", 36.5, 24, 39, 23], ["Q", 41.5, 22, 44.5, 21], ["Q", 47.5, 20, 50, 19], ["Q", 52.5, 18, 55, 17], ["Q", 57.5, 16, 60, 14.5], ["Q", 62.5, 13, 64.5, 12.5], ["Q", 66.5, 12, 68.5, 11.5], ["Q", 70.5, 11, 72, 10], ["Q", 73.5, 9, 76, 8], ["Q", 78.5, 7, 81.5, 5.5], ["Q", 84.5, 4, 87, 3], ["Q", 89.5, 2, 92.5, 1.5], ["Q", 95.5, 1, 99, 0.5], ["Q", 102.5, 0, 107, 0], ["Q", 111.5, 0, 114, 0], ["Q", 116.5, 0, 119.5, 0], ["Q", 122.5, 0, 125, 0], ["Q", 127.5, 0, 131, 1], ["Q", 134.5, 2, 136.5, 3], ["Q", 138.5, 4, 140.5, 5], ["Q", 142.5, 6, 144, 7], ["Q", 145.5, 8, 147.5, 9.5], ["Q", 149.5, 11, 151.5, 12], ["Q", 153.5, 13, 154.5, 14], ["Q", 155.5, 15, 156.5, 16.5], ["Q", 157.5, 18, 158.5, 19], ["Q", 159.5, 20, 160, 21.5], ["Q", 160.5, 23, 161.5, 24.5], ["Q", 162.5, 26, 163.5, 28], ["Q", 164.5, 30, 165, 32], ["Q", 165.5, 34, 166, 35], ["Q", 166.5, 36, 167, 37], ["Q", 167.5, 38, 168.5, 39], ["Q", 169.5, 40, 170, 41.5], ["Q", 170.5, 43, 171, 44.5], ["Q", 171.5, 46, 172, 47.5], ["Q", 172.5, 49, 173.5, 51], ["Q", 174.5, 53, 175.5, 55], ["Q", 176.5, 57, 177, 58.5], ["Q", 177.5, 60, 178, 62], ["Q", 178.5, 64, 179, 64.5], ["Q", 179.5, 65, 179.5, 65.5], ["Q", 179.5, 66, 179.5, 66.5], ["Q", 179.5, 67, 179.5, 67], ["Q", 179.5, 67, 179.5, 67.5], ["Q", 179.5, 68, 180, 68.5], ["Q", 180.5, 69, 180.5, 70], ["Q", 180.5, 71, 180.5, 72], ["Q", 180.5, 73, 180.5, 74], ["Q", 180.5, 75, 180.5, 75.5], ["Q", 180.5, 76, 180.5, 76.5], ["Q", 180.5, 77, 181, 77], ["L", 181.5, 77]], "shadow": null, "pathOffset": {"y": 0, "x": 0}, "left": 161.75}], "background": ""}'


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
        db.cursor().execute(model.DB_DROP_TABLES)
        db.commit()
        db.cursor().execute(model.PROMPT_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(model.IMAGE_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(model.GAME_TABLE_SCHEMA)
        db.commit()


def requires_username(view):
    pass
    @wraps(view)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            fakenames = ['Homer', 'Marge', 'Bart', 'Lisa', 'Maggie', 'Krusty',
                         'Itchy', 'Scratchy', 'Dr. Hibbert', 'Nelson', 'Jimbo']
            session['username'] = random.sample(fakenames, 1)[0]

        return view(*args, **kwargs)
    return decorated


@requires_username
def get_first_prompt():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        #username = session['username']
        cur.execute(model.DB_GET_FIRST_PROMPT_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(model.DB_GET_FIRST_PROMPT_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        first_prompts = p1.intersection(p2)
        db.commit()
    if first_prompts:
        result = first_prompts.pop()
        session['game_id'] = result[1]
    # If there is no game in the DB with no first prompt not contributed
    # by username, repeat the above game-fetching and selecting logic after
    # making a game.
    # This COULD be a much shorter while loop,
    # but that would make it harder to debug.
    else:
        create_game_on_step_two()
        # Repeat the above, but after creating a game.
        with closing(connect_db()) as db:
            cur = db.cursor()
            username = session['username']
            cur.execute(model.DB_GET_FIRST_PROMPT_A, [username])
            #prompts from games not yet contributed to by user
            p1 = set(cur.fetchall())
            cur.execute(model.DB_GET_FIRST_PROMPT_B)
            #prompts from games needing user input for next step
            p2 = set(cur.fetchall())
            first_prompts = p1.intersection(p2)
            db.commit()
            result = first_prompts.pop()
            session['game_id'] = result[1]
    # This is the culmination of both sides of the conditional:
    return result[0]


@requires_username
def get_second_prompt():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(model.DB_GET_SECOND_PROMPT_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(model.DB_GET_SECOND_PROMPT_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        second_prompts = p1.intersection(p2)
        db.commit()
    if second_prompts:
        result = second_prompts.pop()
        session['game_id'] = result[1]
        return result[0]
    return "Database could not find an appopriate game"


@requires_username
def get_first_image():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(model.DB_GET_FIRST_IMAGE_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(model.DB_GET_FIRST_IMAGE_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        first_images = p1.intersection(p2)
        db.commit()
    if first_images:
        result = first_images.pop()
        session['game_id'] = result[1]
        return result[0]
    return sorry_image


@requires_username
def get_second_image():
    #Retrieves a first prompt from a game that the user has not contributed to.
    with closing(connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(model.DB_GET_SECOND_IMAGE_A, [username])
        #prompts from games not yet contributed to by user
        p1 = set(cur.fetchall())
        cur.execute(model.DB_GET_SECOND_IMAGE_B)
        #prompts from games needing user input for next step
        p2 = set(cur.fetchall())
        second_images = p1.intersection(p2)
        db.commit()
    if second_images:
        result = second_images.pop()
        session['game_id'] = result[1]
        return result[0]
    return sorry_image


@requires_username
def create_game():
    # execute a DB_CREATE_GAME script, RETURNING id for the game
    with closing(connect_db()) as db:
        cur = db.cursor()
        cur.execute(model.DB_CREATE_GAME)
        game_id = cur.fetchone()[0]
        db.commit()
        return game_id


@requires_username
def create_game_on_step_two():
        ''' Chain together create_game() and store_data() using
        a randomly chosen default string as the first prompt.
        Called when a user has submitted their own prompt and
        needs to see a different user's prompt, but there are no
        other users' prompts -- so a default prompt must be
        created for them. '''

        # Note: We DO NOT need to call create_game() because store_data()
        # does that for us, and it also handles
        # cookie attribute assignment and accessing.
        # To be precise, store_data() puts the game_id inside the session
        # and also uses it, along with the preexisting session username,
        # to submit a prompt as if it was that user's prompt.

        # This function will autogenerate a first prompt for the user.
        list_of_default_prompts = ['A red shield decorated with two arrows and a slash.',
                                   'A smurf and a carebear walk into a bar...',
                                   'Dark Side Story']
        random_prompt = random.sample(list_of_default_prompts, 1)[0]
        # NOTE: default_username is only used in functions like this,
        # where default prompts are to be provided.
        # This parameterization allows us to call store_data() this way
        # for any step where a user needs a default prompt supplied.
        store_data('first_prompt_id',
                   'prompts',
                   random_prompt,
                   default_username="A figment of your imagination")



@requires_username
def store_data(game_column, tablename, data, default_username=None):
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

        if default_username is not None:
            # The newly-created first prompt MAY NOT BE created
            # by the same user who is going to reply to it
            username = str(default_username)
        else:
            username = session['username']

        now = datetime.datetime.utcnow()
        if tablename == 'prompts':
            cur.execute(model.DB_INSERT_PROMPT,
                        [username, data, now])
        elif tablename == 'images':
            cur.execute(model.DB_INSERT_IMAGE,
                        [username, data, now])
        inserted_data_id = cur.fetchone()[0]

        # "Postgres made us do it." -- Jason
        execute_string = model.DB_UPDATE_GAMES % (game_column,
                                                  '%s', session['game_id'])
        cur.execute(execute_string,
                    [inserted_data_id])
        db.commit()


@requires_username
def get_games():
    """Return a list of dictionaries containing gameids for games that
    the current user has contributed to"""
    GET_PROMPTS = "SELECT id FROM prompts WHERE username=%s"
    GET_IMAGES = "SELECT id FROM images WHERE username=%s"
    GET_GAMES_P = "SELECT id FROM games WHERE first_prompt_id=%s OR second_prompt_id=%s OR third_prompt_id=%s"
    GET_GAMES_I = "SELECT id FROM games WHERE first_image_id=%s OR second_image_id=%s"
    GET_DATA_IDS = "SELECT * FROM games WHERE id=%s"
    with closing(connect_db()) as db:
        cur = db.cursor()
        username = session['username']
        cur.execute(GET_PROMPTS, [username])
        prompt_ids = cur.fetchall()
        cur.execute(GET_IMAGES, [username])
        image_ids = cur.fetchall()
        games = []
        for i_d in prompt_ids:
            cur.execute(GET_GAMES_P, [i_d, i_d, i_d])
            games += cur.fetchall()
        for i_d in image_ids:
            cur.execute(GET_GAMES_I, [i_d, i_d])
            games += cur.fetchall()
        #Cleanup! Gets rid of duplicates and returns a list of ints rather than tuples
        games = [game[0] for game in list(set(games))]
        #Now we fetch a list of ids of prompts/images for each game that the user
        #has contributed to
        game_data_ids = []
        for g in games:
            cur.execute(GET_DATA_IDS, [g])
            game_data_ids.append(cur.fetchall())
            db.commit()
        game_data_ids = [gdi[0] for gdi in game_data_ids]
        #We have the ids of all data we need, in order. Now we fetch the actual data
        def build_dict(game):
            keys = ['id', 'first_prompt', 'first_image', 'second_prompt', 'second_image', 'third_prompt']
            i_d = game[0]
            cur.execute("SELECT data FROM prompts WHERE id=%s", [game[1]])
            first_prompt = cur.fetchall()
            cur.execute("SELECT data FROM images WHERE id=%s", [game[2]])
            first_image = cur.fetchall()
            cur.execute("SELECT data FROM prompts WHERE id=%s", [game[3]])
            second_prompt = cur.fetchall()
            cur.execute("SELECT data FROM images WHERE id=%s", [game[4]])
            second_image = cur.fetchall()
            cur.execute("SELECT data FROM prompts WHERE id=%s", [game[5]])
            third_prompt = cur.fetchall()
            values = [i_d, first_prompt, first_image, second_prompt, second_image, third_prompt]
            for i in range(1, 6):
                if len(values[i]) == 0:
                    values[i] = None
                elif len(values[i]) == 1:
                    values[i] = values[i][0][0]
            result = dict(zip(keys, values))
            if result['first_image'] is None:
                result['first_image'] = sorry_image
            if result['second_image'] is None:
                result['second_image'] = sorry_image

            return result
        db.commit()
        games = [build_dict(game) for game in game_data_ids]
        return games

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
    print json.dumps(request.json)
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
