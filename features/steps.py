import lettuce

from flask import url_for
from app import app
import json
from game import init_db


@lettuce.before.all
def setup_app():
    print "This happens before all the lettuce tests begin"
    app.config['DATABASE'] = "dbname=travis_ci_test  user=postgres"
    init_db()
    app.config['TESTING'] = True


@lettuce.after.all
def teardown_app(total):
    print "This happens after all the lettuce tests have run"


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


@lettuce.step('I submit a new prompt')
def posts_prompt(step):
    lettuce.world.response = \
        lettuce.world.client.post('/step_two', data={'prompt': 'New thing'})


@lettuce.step('I see the second page')
def see_step_two(step):
    body = json.loads(lettuce.world.response.data)['html']
    msg1 = "found prompt-entry form in %s"
    msg2 = "did not find drawing canvas form in %s"
    assert 'id="prompt-entry"' not in body, msg1 % body
    assert 'canvas id="drawing"' in body, msg2 % body


# @lettuce.step('the title "([^"]*)"')
# def title_input(step, title):
#     lettuce.world.title = title


# @lettuce.step('the text "([^"]*)"')
# def text_input(step, text):
#     lettuce.world.text = text


# @lettuce.step('I submit the add form')
# def add_entry(step):
#     entry_data = {
#         'title': lettuce.world.title,
#         'text': lettuce.world.text,
#     }
#     lettuce.world.response = lettuce.world.client.post(
#         '/add', data=entry_data, follow_redirects=False
#     )


# @lettuce.step('I am redirected to the home page')
# def redirected_home(step):
#     with app.test_request_context('/'):
#         home_url = url_for('show_entries')
#     # assert that we have been redirected to the home page
#     assert lettuce.world.response.status_code in [301, 302]
#     assert lettuce.world.response.location == 'http://localhost' + home_url
#     # now, fetch the homepage so we can finish this off.
#     lettuce.world.response = lettuce.world.client.get(home_url)


# @lettuce.step('I do not see my new entry')
# def no_new_entry(step):
#     body = lettuce.world.response.data
#     for val in [lettuce.world.title, lettuce.world.text]:
#         assert val not in body


# @lettuce.step('I see my new entry')
# def yes_new_entry(step):
#     body = lettuce.world.response.data
#     for val in [lettuce.world.title, lettuce.world.text]:
#         assert val in body
