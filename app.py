from __future__ import unicode_literals
from flask import Flask
from flask import render_template
from flask import request
import io
import json

app = Flask(__name__)


def store_drawing(drawing_data):
    tempfile = io.open("stored_drawing.txt", "wb")
    json.dump(drawing_data, tempfile)
    tempfile.close()


def retrieve_drawing():
    tempfile = io.open("stored_drawing.txt", "r")
    drawing_data = json.load(tempfile)
    tempfile.close()
    return drawing_data


@app.route('/')
def show_test_page():
    return render_template('test_page.html')


@app.route('/new-drawing', methods=['POST'])
def receive_drawing():
    last_pic = retrieve_drawing()
    store_drawing(request.json)
    return last_pic

if __name__ == '__main__':
    app.run(debug=True)
