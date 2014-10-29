import lettuce

from flask import url_for
from app import app
import json
from contextlib import closing
import psycopg2
from game import DB_DROP_TABLES, PROMPT_TABLE_SCHEMA, IMAGE_TABLE_SCHEMA,\
    GAME_TABLE_SCHEMA


def init_db():
    """Initialize the database.
    WARNING: This will drop existsing tables"""
    with closing(psycopg2.connect(app.config['DATABASE'])) as db:
        db.cursor().execute(PROMPT_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(IMAGE_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(GAME_TABLE_SCHEMA)
        db.commit()


def clear_db():
    """Clear the database"""
    with closing(psycopg2.connect(app.config['DATABASE'])) as db:
        db.cursor().execute(DB_DROP_TABLES)
        db.commit()


@lettuce.before.all
def setup_app():
    print "This happens before all the lettuce tests begin"
    app.config['DATABASE'] = "dbname=travis_ci_test  user=postgres"
    init_db()
    app.config['TESTING'] = True


@lettuce.after.all
def teardown_app(total):
    print "This happens after all the lettuce tests have run"
    clear_db()


@lettuce.step('a new user')
def new_user(step):
    with app.test_client() as client:
        lettuce.world.client = client


@lettuce.step('I view the home page')
def request_homepage(step):
    with app.test_request_context('/'):
        home_url = url_for('home')
        print home_url
    lettuce.world.response = lettuce.world.client.get(home_url)


@lettuce.step('I see the first page')
def see_step_one(step):
    body = lettuce.world.response.data
    msg1 = "did not find prompt-entry form in %s"
    msg2 = "found drawing canvas form in %s"
    assert 'id="prompt-entry"' in body, msg1 % body
    assert 'canvas id="drawing"' not in body, msg2 % body


@lettuce.step('I can submit a new prompt')
def can_post_prompt(step):
    response = lettuce.world.client.post('/step_two',
                                         data={'prompt': 'New thing'})
    assert response.status_code == 200, response.status_code


@lettuce.step('I submit a new prompt "([^"]*)"')
def posts_prompt(step, prompt):
    lettuce.world.expected_data = prompt
    lettuce.world.response = \
        lettuce.world.client.post('/step_two', data={'prompt': prompt})


@lettuce.step('I see the second page')
def see_step_two(step):
    body = json.loads(lettuce.world.response.data)['html']
    msg1 = "found prompt-entry form in %s"
    msg2 = "did not find drawing canvas form in %s"
    assert 'id="prompt-entry"' not in body, msg1 % body
    assert 'canvas id="drawing"' in body, msg2 % body


@lettuce.step('It is put in the prompts database')
def check_for_database(step):
    with closing(psycopg2.connect(app.config['DATABASE'])) as db:
        cur = db.cursor()
        cur.execute("SELECT data FROM prompts WHERE data=%s",
                    [lettuce.world.expected_data])
        response = cur.fetchall()
        print response
