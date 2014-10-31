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
import default_images
from default_images import sorry_image


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
        db.cursor().execute(model.DB_DROP_TABLES)
        db.commit()
        db.cursor().execute(model.PROMPT_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(model.IMAGE_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(model.GAME_TABLE_SCHEMA)
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
    else:
        create_game_on_step_four()
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
            result = second_prompts.pop()
            session['game_id'] = result[1]
    return result[0]


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
    # This COULD be a much shorter while loop,
    # but that would make it harder to debug.
    else:
        create_game_on_step_three()
        # Repeat the above, but after creating a game.
        with closing(connect_db()) as db:
            cur = db.cursor()
            username = session['username']
            cur.execute(model.DB_GET_FIRST_IMAGE_A, [username])
            #images from games not yet contributed to by user
            p1 = set(cur.fetchall())
            cur.execute(model.DB_GET_FIRST_IMAGE_B)
            #images from games needing user input for next step
            p2 = set(cur.fetchall())
            first_images = p1.intersection(p2)
            db.commit()
            result = first_images.pop()
            session['game_id'] = result[1]
    # This is the culmination of both sides of the conditional:
    return result[0]


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
    else:
        create_game_on_step_five()
        with closing(connect_db()) as db:
            cur = db.cursor()
            username = session['username']
            cur.execute(model.DB_GET_SECOND_IMAGE_A, [username])
            #images from games not yet contributed to by user
            p1 = set(cur.fetchall())
            cur.execute(model.DB_GET_SECOND_IMAGE_B)
            #images from games needing user input for next step
            p2 = set(cur.fetchall())
            second_images = p1.intersection(p2)
            db.commit()
            result = second_images.pop()
            session['game_id'] = result[1]
    return result[0]


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
        list_of_default_prompts = \
            ['A red shield decorated with two arrows and a slash.',
             'A smurf and a carebear walk into a bar...',
             'Dark Side Story']
        random_prompt = random.sample(list_of_default_prompts, 1)[0]
        # NOTE: default_username is only used in functions like this,
        # where default prompts are to be provided.
        # This parameterization allows us to call store_data() this way
        # for any step where a user needs a default prompt supplied.
        created_game_id = store_data('first_prompt_id',
                                     'prompts',
                                     random_prompt,
                                     default_username=
                                     "A figment of your imagination")

        return created_game_id


@requires_username
def create_game_on_step_three():

    # Pull the game up to be ready for step three:
    created_game_id = create_game_on_step_two()

    # Generate a default image:
    list_of_default_images = [default_images.default_image_one]
    random_image = random.sample(list_of_default_images, 1)[0]

    # Now, store this default step 2.
    created_game_id = store_data('first_image_id',
                                 'images',
                                 random_image,
                                 default_username="A spirit of the woods",
                                 supplied_game_id=created_game_id)

    return created_game_id


@requires_username
def create_game_on_step_four():

    # Pull the game up to be ready for step four:
    created_game_id = create_game_on_step_three()

    # This function will autogenerate a second prompt for the user.
    list_of_default_prompts = ['A purple elephant on the computer.',
                               'Standing under your own raincloud.',
                               'Star Wars: The Emperor Talks Back']
    random_prompt = random.sample(list_of_default_prompts, 1)[0]
    # NOTE: default_username is only used in functions like this,
    # where default prompts are to be provided.
    # This parameterization allows us to call store_data() this way
    # for any step where a user needs a default prompt supplied.
    # Store step three:
    created_game_id = store_data('second_prompt_id',
                                 'prompts',
                                 random_prompt,
                                 default_username=
                                 "The elf who lives under the servers",
                                 supplied_game_id=created_game_id)

    return created_game_id


@requires_username
def create_game_on_step_five():

    # Pull the game up to be ready for step four:
    created_game_id = create_game_on_step_four()

    # Generate a default image:
    list_of_default_images = [default_images.default_image_two]
    random_image = random.sample(list_of_default_images, 1)[0]

    # Now, store step 4:
    created_game_id = store_data('second_image_id',
                                 'images',
                                 random_image,
                                 default_username=
                                 "An invisible blue space whale",
                                 supplied_game_id=created_game_id)

    return created_game_id


@requires_username
def store_data(game_column, tablename, data,
               default_username=None, supplied_game_id=None):
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

        # This part is for chaining together default prompt creation.
        # Supplied game IDs are so we can refer to the same game while
        # changing the default username.
        if supplied_game_id is not None:
            game_id_for_database_string = supplied_game_id
        else:
            game_id_for_database_string = session['game_id']

        # "Postgres made us do it." -- Jason
        execute_string = model.DB_UPDATE_GAMES % (game_column,
                                                  '%s',
                                                  game_id_for_database_string)
        cur.execute(execute_string,
                    [inserted_data_id])
        db.commit()
        # When we're making a default-user game,
        # return the game_id.
        # Otherwise don't bother.
        if default_username is not None:
            return game_id_for_database_string


@requires_username
def get_games():
    GET_PROMPTS = "SELECT id FROM prompts WHERE username=%s"
    GET_IMAGES = "SELECT id FROM images WHERE username=%s"
    GET_GAMES_P = """SELECT id FROM games
    WHERE first_prompt_id=%s OR second_prompt_id=%s OR third_prompt_id=%s"""
    GET_GAMES_I = """SELECT id FROM games
    WHERE first_image_id=%s OR second_image_id=%s"""
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
        db.commit()
    #Cleanup! Gets rid of duplicates and returns a list of ints not tuples
    return [game[0] for game in list(set(games))]


def get_game_by_id(eyedee):
    with closing(connect_db()) as db:
        cur = db.cursor()
        GET_DATA_IDS = "SELECT * FROM games WHERE id=%s"
        cur.execute(GET_DATA_IDS, [eyedee])
        game_data = cur.fetchall()[0]
        #We have the ids of data we need, in order. Now fetch the actual data

        def build_dict(game):
            keys = ['id', 'first_prompt', 'first_image', 'second_prompt',
                    'second_image', 'third_prompt']
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
            values = [i_d, first_prompt, first_image, second_prompt,
                      second_image, third_prompt]
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
        game_dict = build_dict(game_data)
        db.commit()
        return game_dict


def get_all_game_ids():
    with closing(connect_db()) as db:
        cur = db.cursor()
        cur.execute('SELECT id FROM games')
        ids = cur.fetchall()

    return [i_d[0] for i_d in ids]


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
                           list=games)


@app.route('/game/<int:game_id>')
def show_game(game_id):
    if 'X-Requested-With' in request.headers:
        return json.dumps(get_game_by_id(game_id))
    allids = get_all_game_ids()
    if game_id not in allids:
        return redirect(url_for('show_games'))
    allids.remove(game_id)
    allids.insert(0, game_id)
    return render_template('show_games.html',
                           user="Anyone",
                           list=allids)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username'].encode('utf-8')
        return redirect(url_for('home'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
