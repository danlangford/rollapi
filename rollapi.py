import logging
import dice
from flask import Flask
from flask import request
from flask import jsonify


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
    body = request.get_json()
    command = body['item']['message']['message'].replace('/roll ','')
    from_name = body['item']['message']['from']['mention_name']
    roll_result = get_roll(command)
    message = '@{} rolling {} gets {}'.format(from_name, command, roll_result)

    return jsonify({'color':'black','message':message,'notify':False,'message_format':'text'})


if __name__ == '__main__':
    app.run()
