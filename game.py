# -*- coding: utf-8 -*-
from flask import Flask
import os
import psycopg2
from contextlib import closing

PROMPT_TABLE_SCHEMA = """
DROP TABLE IF EXISTS prompts;
CREATE TABLE prompts(
    id serial PRIMARY KEY,
    userid INTEGER NOT NULL,
    text VARCHAR(200) NOT NULL,
    created TIMESTAMP NOT NULL
    )
"""

IMAGE_TABLE_SCHEMA = """
DROP TABLE IF EXISTS images;
CREATE TABLE images(
    id serial PRIMARY KEY,
    userid INTEGER NOT NULL,
    imgdata TEXT NOT NULL,
    created TIMESTAMP NOT NULL
    )
"""
# imgdata is datatype TEXT for now--don't know how long these strings will be

GAME_TABLE_SCHEMA = """
DROP TABLE IF EXISTS games;
CREATE TABLE games(
    id serial PRIMARY KEY,
    first_prompt_id INTEGER NOT NULL,
    second_prompt_id INTEGER NOT NULL,
    thrid_prompt_id INTEGER NOT NULL,
    first_image_id INTEGER NOT NULL,
    second_image_id INTEGER NOT NULL
    )
"""


def connect_db(app=Flask(__name__)):
    """Return a connection to the configured database"""
    return psycopg2.connect(app.config['DATABASE'])


def init_db():
    """Initialize the database.
    WARNING: This will drop existsing tables"""
    with closing(connect_db()) as db:
        db.cursor().execute(PROMPT_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(IMAGE_TABLE_SCHEMA)
        db.commit()
        db.cursor().execute(GAME_TABLE_SCHEMA)
        db.commit()
