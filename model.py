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
    data VARCHAR(500) NOT NULL,
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

# The following SQL commands will retrieve data from the database
# A) Will pull all data at the current step from games that the user has not
#    yet contributed to.
# B) WIll pull all data at the current step from games that do not yet have
#    an entry for the next step.
DB_GET_FIRST_PROMPT_A = """
SELECT prompts.data, games.id
FROM games
INNER JOIN prompts
ON games.first_prompt_id=prompts.id
WHERE NOT username=%s
"""
DB_GET_FIRST_PROMPT_B = """
SELECT prompts.data, games.id
FROM games
INNER JOIN prompts
ON games.first_prompt_id=prompts.id
WHERE first_image_id IS NULL
"""
DB_GET_SECOND_PROMPT_A = """
SELECT prompts.data, games.id
FROM games
INNER JOIN prompts
ON games.second_prompt_id=prompts.id
WHERE NOT username=%s
"""
DB_GET_SECOND_PROMPT_B = """
SELECT prompts.data, games.id
FROM games
INNER JOIN prompts
ON games.second_prompt_id=prompts.id
WHERE second_image_id IS NULL
"""
DB_GET_FIRST_IMAGE_A = """
SELECT images.data, games.id
FROM games
INNER JOIN images
ON games.first_image_id=images.id
WHERE NOT username=%s
"""
DB_GET_FIRST_IMAGE_B = """
SELECT images.data, games.id
FROM games
INNER JOIN images
ON games.first_image_id=images.id
WHERE second_prompt_id IS NULL
"""
DB_GET_SECOND_IMAGE_A = """
SELECT images.data, games.id
FROM games
INNER JOIN images
ON games.second_image_id=images.id
WHERE NOT username=%s
"""
DB_GET_SECOND_IMAGE_B = """
SELECT images.data, games.id
FROM games
INNER JOIN images
ON games.second_image_id=images.id
WHERE third_prompt_id IS NULL
"""
