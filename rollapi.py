# coding=utf-8
import dice
from flask import Flask
from flask import request
from flask import jsonify


app = Flask(__name__)


def _get_roll(roll_cmd):
    return dice.roll(roll_cmd)


@app.route('/')
def hello_world():
    return 'an api around the "dice" python lib thrown together real quick by @danlangford'


@app.route('/api/v1/roll/<roll_cmd>')
def get_roll(roll_cmd):
    return str(_get_roll(roll_cmd))


@app.route('/api/v1/hipchat', methods=['POST'])
def hipchat():

    body = request.get_json()
    from_name = body['item']['message']['from']['mention_name']
    slash_command = body['item']['message']['message']

    color='black'
    try:
        # partition #1 removes the command (/roll) and partition #2 isolates the roll syntax from any other message
        roll_syntax, _d, other_msg = slash_command.partition(' ')[3].partition(' ')

        if roll_syntax.lower() == 'help':
            color='blue'
            roll="try things like d6 2d8 1d20+3 4d6^3 2d20v1 5d6s 4d10t where s=sort t=total ^=top_values v=bottom_values"
        else:
            roll = _get_roll(roll_syntax)
    except Exception as be:
        color='red'
        roll = 'Exception: {}'.format(be.message)

    if isinstance(roll, (list,tuple)) and not isinstance(roll, basestring):
        roll_msg = '{} (Σ={})'.format(roll, sum(roll))
    else:
        roll_msg = str(roll)

    message = '@{} {} {}'.format(from_name, roll_msg, other_msg)

    return jsonify({'color':color,'message':message,'notify':False,'message_format':'text'})


if __name__ == '__main__':
    app.run()
