# coding=utf-8
import dice
from flask import Flask
from flask import request
from flask import jsonify


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'an api around the "dice" python lib thrown together real quick by @danlangford'


@app.route('/api/v1/roll/<roll_cmd>')
def get_roll(roll_cmd):
    return str(_get_roll(roll_cmd))


def _get_roll(roll_cmd):
    return dice.roll(roll_cmd)


@app.route('/api/v1/hipchat', methods=['POST'])
def hipchat():
    body = request.get_json()
    from_name = body['item']['message']['from']['mention_name']
    slash_command = body['item']['message']['message'].strip()
    roll_msg, other_msg, color = _hipchat(slash_command)
    message = '@{} {} {}'.format(from_name, roll_msg, other_msg)
    return jsonify({'color':color,'message':message,'notify':False,'message_format':'text'})


def _hipchat(slash_command):
    color='yellow'
    other_msg=''
    try:
        # 1st partition() removes the command (/roll)
        # 2nd partition() isolates the roll syntax from any other message
        roll_syntax, _d, other_msg = slash_command.partition(' ')[2].partition(' ')

        if roll_syntax.lower().strip() in ['help','']:
            color='gray'
            roll='try things like d6 2d8 1d20+3 4d6^3 2d20v1 5d6s 4d10t'
            other_msg='where s=sort t=total ^=top_values v=bottom_values'
        else:
            roll = _get_roll(roll_syntax)
    except Exception as e:
        app.logger.error(e)
        color='red'
        roll = 'Exception: {}'.format(e)

    if isinstance(roll, (list,tuple)) and not isinstance(roll, basestring):
        if len(roll) == 1:
            roll_msg = str(roll[0])
        else:
            roll_msg = '{} (Σ={})'.format(roll, sum(roll))
    else:
        roll_msg = str(roll)

    return roll_msg, other_msg, color


if __name__ == '__main__':
    app.run()
