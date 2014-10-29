# -*- coding: utf-8 -*-
from flask import Flask
import os
import psycopg2
from contextlib import closing

DB_DROP_TABLES = """
DROP TABLE IF EXISTS games, prompts, images;
"""

PROMPT_TABLE_SCHEMA = """
CREATE TABLE "prompts" (
    id serial PRIMARY KEY,
    username TEXT NOT NULL,
    data VARCHAR(MAX) NOT NULL,
    created TIMESTAMP NOT NULL
    )
"""

IMAGE_TABLE_SCHEMA = """
CREATE TABLE "images" (
    id serial PRIMARY KEY,
    username TEXT NOT NULL,
    data TEXT NOT NULL,
    created TIMESTAMP NOT NULL
    )
"""
# imgdata is datatype TEXT for now--don't know how long these strings will be

GAME_TABLE_SCHEMA = """
CREATE TABLE "games" (
    id serial PRIMARY KEY,
    first_prompt_id INTEGER REFERENCES prompts,
    first_image_id INTEGER REFERENCES images,
    second_prompt_id INTEGER REFERENCES prompts,
    second_image_id INTEGER REFERENCES images,
    third_prompt_id INTEGER REFERENCES prompts
    )
"""

DB_CREATE_GAME = """
INSERT INTO games (
    first_prompt_id,
    first_image_id,
    second_prompt_id,
    second_image_id,
    third_prompt_id)
VALUES (
    NULL,
    NULL,
    NULL,
    NULL,
    NULL)
RETURNING id
"""


# Generic PSQL update-game-content string.
# Can be divided into separate image
# and prompt versions, if desired.
DB_INSERT_IMAGE = """
INSERT INTO images (username, data, created) VALUES (%s, %s, %s) RETURNING id
"""
# Usage:
# tablename, (datatypenameinPSQL), (username, Flask_data_name, created)
# Example:
# INSERT INTO images (username, imgdata, created)
#   VALUES (session['username'], jsonified_image_data(?), datetime.now())

DB_INSERT_PROMPT = """
INSERT INTO prompts (username, data, created) VALUES (%s, %s, %s) RETURNING id
"""

# update games table to have this new id in the correct slot
DB_UPDATE_GAMES = """
UPDATE games SET %s=%s WHERE id=%s
"""
# UPDATE games SET game_column=inserted_data_id WHERE id=session['game_id']


def connect_db(app=Flask(__name__)):
    """Return a connection to the configured database"""
    if 'DATABASE' not in app.config:
        app.config['DATABASE'] = os.environ.get(
            'DATABASE_URL', 'dbname=telephone_db user=store')

    return psycopg2.connect(app.config['DATABASE'])


def init_db():
    """Initialize the database.
    WARNING: This will drop existsing tables"""
    with closing(connect_db()) as db:
        db.cursor().execute(DB_DROP_TABLES)
        db.commit()
        db.cursor().execute(PROMPT_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(IMAGE_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(GAME_TABLE_SCHEMA)
        db.commit()
