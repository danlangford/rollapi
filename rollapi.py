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
    roll_syntax, _d, other_msg = body['item']['message']['message'].replace('/roll ','').partition(' ')

    roll = _get_roll(roll_syntax)

    if isinstance(roll, (list,tuple)) and not isinstance(roll, basestring):
        roll_msg = '{} (Σ={})'.format(roll, sum(roll))
    else:
        roll_msg = str(roll)

    if len(other_msg)>0:
        fluff = 'says "{}" with'.format(other_msg)
    else:
        fluff = 'rolling {} gets'.format(roll_syntax)

    message = '@{} {} {}'.format(from_name, fluff, roll_msg)

    return jsonify({'color':'black','message':message,'notify':False,'message_format':'text'})


if __name__ == '__main__':
    app.run()
