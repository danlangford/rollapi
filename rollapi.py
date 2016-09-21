import logging
import dice
from flask import Flask
from flask import request
from flask import json
from flask import Response


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/v1/roll/<roll_cmd>')
def get_roll(roll_cmd):
    return str(dice.roll(roll_cmd))

@app.route('/api/v1/hipchat', methods=['POST'])
def hipchat():
    log = app.logger
    log.debug( 'hi' )
    log.debug(request.get_json())

    log.debug(request.json)
    return request.json['item']['message']['message']


if __name__ == '__main__':
    app.run()
